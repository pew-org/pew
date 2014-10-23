#! /usr/bin/env python

from __future__ import print_function, absolute_import

import os
import sys
import argparse
import shutil
import random
import textwrap
from subprocess import CalledProcessError
from pathlib import Path

try:
    from clonevirtualenv import clone_virtualenv
except ImportError:
    pass # setup.py needs to import this before the dependencies are installed

from pew import __version__
from pew._utils import (check_call, invoke, expandpath, own,
                        env_bin_dir, check_path, which, temp_environ)

windows = sys.platform == 'win32'


def update_args_dict():
    global args
    args = dict(enumerate(sys.argv))

update_args_dict()

workon_home = expandpath(
    os.environ.get('WORKON_HOME',
                   os.path.join(os.environ.get('XDG_DATA_HOME',
                                               '~/.local/share'),
                                'virtualenvs')))


def makedirs_and_symlink_if_needed(workon_home):
    if not workon_home.exists() and own(workon_home):
        workon_home.mkdir(parents=True)
        link = expandpath('~/.virtualenvs')
        if os.name == 'posix' and 'WORKON_HOME' not in os.environ and \
           'XDG_DATA_HOME' not in os.environ and not link.exists():
            try:
                workon_home.symlink_to(str(link))
            except OSError as e:
                # FIXME on TravisCI, even if I check with `link.exists()`, this
                # exception can be raised and needs to be catched, maybe it's a race condition?
                if e.errno != 17:
                    raise

makedirs_and_symlink_if_needed(workon_home)


inve_site = Path(__file__).parent


def deploy_completions():
    completions = {'complete.bash': Path('/etc/bash_completion.d/pew'),
                   'complete.zsh': Path('/usr/local/share/zsh/site-functions/_pew'),
                   'complete.fish': Path('/etc/fish/completions/pew.fish')}
    for comp, dest in completions.items():
        if not dest.parent.exists():
            dest.parent.mkdir(parents=True)
        shutil.copy(str(inve_site / 'complete_scripts' / comp), str(dest))


def get_project_dir(env):
    project_dir = None
    project_file = workon_home / env / '.project'
    if project_file.exists():
        with project_file.open() as f:
            project_dir = f.readline().strip()

    return project_dir


def unsetenv(key):
    if key in os.environ:
        del os.environ[key]

def inve(env, *args, **kwargs):
    assert args
    # we don't strictly need to restore the environment, since pew runs in
    # its own process, but it feels like the right thing to do
    with temp_environ():
        envdir = workon_home / env
        os.environ['VIRTUAL_ENV'] = str(envdir)
        os.environ['PATH'] = os.pathsep.join([
            str(envdir / env_bin_dir),
            os.environ['PATH'],
        ])

        unsetenv('PYTHONHOME')
        unsetenv('__PYVENV_LAUNCHER__')

        try:
            return check_call(args, shell=windows, **kwargs)
            # need to have shell=True on windows, otherwise the PYTHONPATH
            # won't inherit the PATH
        except OSError as e:
            if e.errno == 2:
                print(kwargs)
                sys.stderr.write("Unable to find %s\n" % args[0])
            else:
                raise


def shell(env, cwd=None):
    shell = 'powershell' if windows else os.environ['SHELL']
    if not windows:
        # On Windows the PATH is usually set with System Utility
        # so we won't worry about trying to check mistakes there
        py = which('python' + str(sys.version_info[0])) # external python
        shell_check = (py + ' -c "from pew.pew import '
                       'prevent_path_errors; prevent_path_errors()"')
        try:
            inve(str(env), shell, '-c', shell_check)
        except CalledProcessError:
            return
    or_ctrld = '' if windows else "or 'Ctrl+D' "
    sys.stderr.write("Launching subshell in virtual environment. Type "
                     "'exit' %sto return.\n" % or_ctrld)

    inve(str(env), shell, cwd=cwd)


def mkvirtualenv(envname, python=None, packages=[], project=None,
                 requirements=None, rest=[]):

    if python:
        rest = ["--python=%s" % python] + rest

    try:
        check_call(["virtualenv", envname] + rest, cwd=str(workon_home))

        if project:
            setvirtualenvproject(envname, project.absolute())

        if requirements:
            inve(envname, 'pip', 'install', '--allow-all-external', '-r', str(expandpath(requirements)))

        if packages:
            inve(envname, 'pip', 'install', '--allow-all-external', *packages)

    except CalledProcessError:
        rmvirtualenvs([envname])
        raise


def mkvirtualenv_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--python')
    parser.add_argument('-i', action='append', dest='packages', help='Install \
a package after the environment is created. This option may be repeated.')
    parser.add_argument('-r', dest='requirements', help='Provide a pip \
requirements file to install a base set of packages into the new environment.')
    parser.add_argument('-d', '--dont-activate', action='store_false',
                        default=True, dest='activate', help="After \
                        creation, continue with the existing shell (don't \
                        activate the new environment).")
    return parser


def new_cmd():
    """Create a new environment, in $WORKON_HOME."""
    parser = mkvirtualenv_argparser()
    parser.add_argument('-a', dest='project', help='Provide a full path to a \
project directory to associate with the new environment.')

    parser.add_argument('envname')
    args, rest = parser.parse_known_args()
    project = expandpath(args.project) if args.project else None

    mkvirtualenv(args.envname, args.python, args.packages, project,
                 args.requirements, rest)
    if args.activate:
        shell(args.envname)


def rmvirtualenvs(envs):
    for env in envs:
        env = workon_home / env
        if os.environ.get('VIRTUAL_ENV') == str(env):
            print("ERROR: You cannot remove the active environment \
(%s)." % env, file=sys.stderr)
            break
        try:
            shutil.rmtree(str(env))
        except OSError as e:
            print("Error while trying to remove the {0} env: \
\n{1}".format(env, e.strerror), file=sys.stderr)


def rm_cmd():
    """Remove one or more environment, from $WORKON_HOME."""
    if len(sys.argv) < 2:
        sys.exit("Please specify an environment")
    rmvirtualenvs(sys.argv[1:])


def showvirtualenv(env):
    print(env)


def show_cmd():
    try:
        showvirtualenv(sys.argv[1])
    except IndexError:
        if 'VIRTUAL_ENV' in os.environ:
            showvirtualenv(Path(os.environ['VIRTUAL_ENV']).name)
        else:
            sys.exit('pew-show [env]')


def lsenvs():
    return sorted(set(env.parts[-3] for env in
                      workon_home.glob(os.path.join('*', env_bin_dir, 'python*'))))


def lsvirtualenv(verbose):
    envs = lsenvs()

    if not verbose:
        print(*envs, sep=' ')
    else:
        for env in envs:
            showvirtualenv(env)


def ls_cmd():
    """List available environments."""
    parser = argparse.ArgumentParser()
    p_group = parser.add_mutually_exclusive_group()
    p_group.add_argument('-b', '--brief', action='store_false')
    p_group.add_argument('-l', '--long', action='store_true')
    args = parser.parse_args()
    lsvirtualenv(args.long)


def workon_cmd():
    """List or change working virtual environments."""
    try:
        env = sys.argv[1]
    except IndexError:
        lsvirtualenv(False)
        return

    env_path = workon_home / env
    if not env_path.exists():
        sys.exit("ERROR: Environment '{0}' does not exist. Create it with \
'pew-new {0}'.".format(env))
    else:

        # Check if the virtualenv has an associated project directory and in
        # this case, use it as the current working directory.
        project_dir = get_project_dir(env) or os.getcwd()
        shell(env, cwd=project_dir)


def sitepackages_dir():
    if 'VIRTUAL_ENV' not in os.environ:
        sys.exit('ERROR: no virtualenv active')
    else:
        return Path(invoke('python', '-c', 'import distutils; \
print(distutils.sysconfig.get_python_lib())').out)


def add_cmd():
    """Add the specified directories to the Python path for the currently active virtualenv.

This will be done by placing the directory names in a path file named
"virtualenv_path_extensions.pth" inside the virtualenv's site-packages
directory; if this file does not exists, it will be created first.

"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='remove', action='store_true')
    parser.add_argument('dirs', nargs='+')
    args = parser.parse_args()

    extra_paths = sitepackages_dir() / '_virtualenv_path_extensions.pth'
    new_paths = [os.path.abspath(d) + u"\n" for d in args.dirs]
    if not extra_paths.exists():
        with extra_paths.open('w') as extra:
            extra.write(u'''import sys; sys.__plen = len(sys.path)
import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)
            ''')

    def rewrite(f):
        with extra_paths.open('r+') as extra:
            to_write = f(extra.readlines())
            extra.seek(0)
            extra.truncate()
            extra.writelines(to_write)

    if args.remove:
        rewrite(lambda ls: [line for line in ls if line not in new_paths])
    else:
        rewrite(lambda lines: lines[0:1] + new_paths + lines[1:])


def sitepackages_dir_cmd():
    print(sitepackages_dir())


def lssitepackages_cmd():
    """Show the content of the site-packages directory of the current virtualenv."""
    site = sitepackages_dir()
    print(*site.iterdir())
    extra_paths = site / '_virtualenv_path_extensions.pth'
    if extra_paths.exists():
        print('from _virtualenv_path_extensions.pth:')
        with extra_paths.open() as extra:
            print(''.join(extra.readlines()))


def toggleglobalsitepackages_cmd():
    """Toggle the current virtualenv between having and not having access to the global site-packages."""
    quiet = args.get(1) == '-q'
    site = sitepackages_dir()
    ngsp_file = site.parent / 'no-global-site-packages.txt'
    if ngsp_file.exists():
        ngsp_file.unlink()
        if not quiet:
            print('Enabled global site-packages')
    else:
        with ngsp_file.open('w'):
            if not quiet:
                print('Disabled global site-packages')


def cp_cmd():
    """Duplicate the named virtualenv to make a new one."""
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('target', nargs='?')
    parser.add_argument('-d', '--dont-activate', action='store_false',
                        default=True, dest='activate', help="After \
                        creation, continue with the existing shell (don't \
                        activate the new environment).")

    args = parser.parse_args()
    source = expandpath(args.source)
    if not source.exists():
        source = workon_home / args.source
        if not source.exists():
            sys.exit('Please provide a valid virtualenv to copy')

    target_name = args.target or source.name

    target = workon_home / target_name

    if target.exists():
        sys.exit('%s virtualenv already exists in %s.' % (target_name, workon_home))

    print('Copying {0} in {1}'.format(source, target_name))
    clone_virtualenv(str(source), str(target))
    if args.activate:
        shell(target_name)


def setvirtualenvproject(env, project):
    print('Setting project for {0} to {1}'.format(env, project))
    with (workon_home / env / '.project').open('wb') as prj:
        prj.write(str(project).encode())


def setproject_cmd():
    """Given a virtualenv directory and a project directory, set the virtualenv up to be associated with the project."""
    env = os.environ.get('VIRTUAL_ENV', args.get(1))
    project = args.get(2, os.path.abspath('.'))
    if not env:
        sys.exit('pew-setproject [virtualenv_path] [project_path]')
    setvirtualenvproject(env, project)


def mkproject_cmd():
    """Create a new project directory and its associated virtualenv."""
    if '-l' in sys.argv or '--list' in sys.argv:
        templates = [t.name[9:] for t in workon_home.glob("template_*")]
        print("Available project templates:", *templates, sep='\n')
        return

    parser = mkvirtualenv_argparser()
    parser.add_argument('envname')
    parser.add_argument(
        '-t', action='append', default=[], dest='templates', help='Multiple \
templates may be selected.  They are applied in the order specified on the \
command line.')
    parser.add_argument(
        '-l', '--list', action='store_true', help='List available templates.')

    args, rest = parser.parse_known_args()

    projects_home = Path(os.environ.get('PROJECT_HOME', '.'))
    if not projects_home.exists():
        sys.exit('ERROR: Projects directory %s does not exist. \
Create it or set PROJECT_HOME to an existing directory.' % projects_home)

    project = (projects_home / args.envname).absolute()
    if project.exists():
        sys.exit('Project %s already exists.' % args.envname)

    mkvirtualenv(args.envname, args.python, args.packages, project.absolute(),
                        args.requirements, rest)

    project.mkdir()

    for template_name in args.templates:
        template = workon_home / ("template_" + template_name)
        inve(args.envname, str(template), args.envname, str(project))
    if args.activate:
        shell(args.envname, cwd=str(project))


def mktmpenv_cmd():
    """Create a temporary virtualenv."""
    parser = mkvirtualenv_argparser()
    env = '.'
    while (workon_home / env).exists():
        env = hex(random.getrandbits(64))[2:-1]

    args, rest = parser.parse_known_args()

    mkvirtualenv(env, args.python, args.packages, requirements=args.requirements,
                 rest=rest)
    print('This is a temporary environment. It will be deleted when you exit')
    try:
        if args.activate:
            # only used for testing on windows
            shell(env)
    finally:
        rmvirtualenvs([env])


def wipeenv_cmd():
    """Remove all installed packages from the current env."""
    pkgs = map(lambda d: d.split("==")[0], invoke('pip', 'freeze').out.split())
    to_remove = [pkg for pkg in pkgs if pkg not in ('distribute', 'wsgiref')]
    if to_remove:
        print("Uninstalling packages:\n%s" % "\n".join(to_remove))
        check_call(['pip', 'uninstall', '-y'] + to_remove)
    else:
        print("Nothing to remove")


def inall_cmd():
    """Run a command in each virtualenv."""
    envs = lsenvs()
    for env in envs:
        print("\n%s:" % env)
        inve(env, *sys.argv[1:])


def in_cmd():
    """Run a command in the given virtualenv."""

    if len(sys.argv) < 2:
        sys.exit('You must provide a valid virtualenv to target')

    env = sys.argv[1]
    env_path = workon_home / env
    if not env_path.exists():
        sys.exit("ERROR: Environment '{0}' does not exist. Create it with \
'pew-new {0}'.".format(env))

    inve(env, *sys.argv[2:])


def restore_cmd():
    """Try to restore a broken virtualenv by reinstalling the same python version on top of it"""

    if len(sys.argv) < 2:
        sys.exit('You must provide a valid virtualenv to target')

    env = sys.argv[1]
    py = workon_home / env / env_bin_dir / ('python.exe' if windows else 'python')
    exact_py = py.resolve().name

    check_call(["virtualenv", env, "--python=%s" % exact_py], cwd=str(workon_home))


def version_cmd():
    """Prints current pew version"""
    print(__version__)


def prevent_path_errors():
    if 'VIRTUAL_ENV' in os.environ and not check_path():
        sys.exit('''ERROR: The virtualenv hasn't been activated correctly.
Either the env is corrupted (try running `pew restore env`),
Or an upgrade of your Python version broke your env,
Or check the contents of your $PATH. You might be adding new directories to it
from inside your shell's configuration file.
In this case, for further details please see: https://github.com/berdario/pew#the-environment-doesnt-seem-to-be-activated''')


def pew():
    cmds = dict((cmd[:-4], fun)
                for cmd, fun in globals().items() if cmd.endswith('_cmd'))
    if sys.argv[1:]:
        try:
            command = cmds[sys.argv[1]]
            sys.argv = ['-'.join(sys.argv[:2])] + sys.argv[2:]
            update_args_dict()
            try:
                return command()
            except CalledProcessError as e:
                return e.returncode
        except KeyError:
            print("ERROR: command %s does not exist." % sys.argv[1],
                  file=sys.stderr)

    longest = max(map(len, cmds)) + 3
    columns = getattr(shutil, 'get_terminal_size', lambda: (80, 24))()[0]

    print('Available commands:\n')
    for cmd, fun in cmds.items():
        if fun.__doc__:
            print(textwrap.fill(
                fun.__doc__.splitlines()[0],
                columns,
                initial_indent=(' {0}: '.format(cmd)).ljust(longest),
                subsequent_indent=longest * ' '))
        else:
            print(' ' + cmd)
