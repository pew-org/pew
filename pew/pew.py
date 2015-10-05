#! /usr/bin/env python

from __future__ import print_function, absolute_import, unicode_literals

import os
import sys
import argparse
import shutil
import random
import textwrap
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
from pathlib import Path

try:
    from shutil import get_terminal_size
except ImportError:
    from backports.shutil_get_terminal_size import get_terminal_size

windows = sys.platform == 'win32'

from clonevirtualenv import clone_virtualenv
if not windows:
    from pythonz.commands.install import InstallCommand
    from pythonz.installer.pythoninstaller import PythonInstaller, AlreadyInstalledError
    from pythonz.commands.list import ListCommand as ListPythons
    from pythonz.commands.locate import LocateCommand as LocatePython
else:
    # Pythonz does not support windows
    InstallCommand = ListPythons = LocatePython = \
        lambda : sys.exit('Command not supported on this platform')

from pew import __version__
from pew._utils import (check_call, invoke, expandpath, own,
                        env_bin_dir, check_path, temp_environ)
from pew._print_utils import print_virtualenvs

if sys.version_info[0] == 2:
    input = raw_input


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
             link.symlink_to(str(workon_home))
        return True
    else:
        return False

pew_site = Path(__file__).parent

def supported_shell():
    shell = Path(os.environ.get('SHELL', '')).stem
    if shell in ('bash', 'zsh', 'fish'):
        return shell


def shell_config_cmd(argv):
    "Prints the path for the current $SHELL helper file"
    shell = supported_shell()
    if shell:
        print(pew_site / 'shell_config' / ('init.' + shell))
    else:
        print('Completions and prompts are unavailable for %s' %
              repr(os.environ.get('SHELL', '')), file=sys.stderr)


def deploy_completions():
    completions = {'complete.bash': Path('/etc/bash_completion.d/pew'),
                   'complete.zsh': Path('/usr/local/share/zsh/site-functions/_pew'),
                   'complete.fish': Path('/etc/fish/completions/pew.fish')}
    for comp, dest in completions.items():
        if not dest.parent.exists():
            dest.parent.mkdir(parents=True)
        shutil.copy(str(pew_site / 'shell_config' / comp), str(dest))


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


def compute_path(env):
    envdir = workon_home / env
    return os.pathsep.join([
        str(envdir / env_bin_dir),
        os.environ['PATH'],
    ])


def inve(env, command, *args, **kwargs):
    """Run a command in the given virtual environment.

    Pass additional keyword arguments to ``subprocess.check_call()``."""
    # we don't strictly need to restore the environment, since pew runs in
    # its own process, but it feels like the right thing to do
    with temp_environ():
        os.environ['VIRTUAL_ENV'] = str(workon_home / env)
        os.environ['PATH'] = compute_path(env)

        unsetenv('PYTHONHOME')
        unsetenv('__PYVENV_LAUNCHER__')

        try:
            return check_call([command] + list(args), shell=windows, **kwargs)
            # need to have shell=True on windows, otherwise the PYTHONPATH
            # won't inherit the PATH
        except OSError as e:
            if e.errno == 2:
                sys.stderr.write("Unable to find %s\n" % command)
            else:
                raise


def fork_shell(env, shellcmd, cwd):
    or_ctrld = '' if windows else "or 'Ctrl+D' "
    sys.stderr.write("Launching subshell in virtual environment. Type "
                     "'exit' %sto return.\n" % or_ctrld)

    inve(env, *shellcmd, cwd=cwd)


def fork_bash(env, cwd):
    # bash is a special little snowflake, and prevent_path_errors cannot work there
    # https://github.com/berdario/pew/issues/58#issuecomment-102182346
    bashrcpath = expandpath('~/.bashrc')
    if bashrcpath.exists():
        with NamedTemporaryFile('w+') as rcfile:
            with bashrcpath.open() as bashrc:
                rcfile.write(bashrc.read())
            rcfile.write('\nexport PATH=' + compute_path(env))
            rcfile.flush()
            fork_shell(env, ['bash', '--rcfile', rcfile.name], cwd)
    else:
        fork_shell(env, ['bash'], cwd)


def shell(env, cwd=None):
    env = str(env)
    shell = os.environ.get('SHELL', 'powershell' if windows else 'sh')
    shell_name = Path(shell).stem
    if shell_name not in ('powershell', 'bash'):
        # On Windows the PATH is usually set with System Utility
        # so we won't worry about trying to check mistakes there
        shell_check = (sys.executable + ' -c "from pew.pew import '
                       'prevent_path_errors; prevent_path_errors()"')
        try:
            inve(env, shell, '-c', shell_check)
        except CalledProcessError:
            return
    if shell_name == 'bash':
        fork_bash(env, cwd)
    else:
        fork_shell(env, [shell], cwd)


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

    except (CalledProcessError, KeyboardInterrupt):
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


def new_cmd(argv):
    """Create a new environment, in $WORKON_HOME."""
    parser = mkvirtualenv_argparser()
    parser.add_argument('-a', dest='project', help='Provide a full path to a \
project directory to associate with the new environment.')

    parser.add_argument('envname')
    args, rest = parser.parse_known_args(argv)
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


def rm_cmd(argv):
    """Remove one or more environment, from $WORKON_HOME."""
    if len(argv) < 1:
        sys.exit("Please specify an environment")
    rmvirtualenvs(argv)


def packages(site_packages):
    nodes = site_packages.iterdir()
    return set([x.stem.split('-')[0] for x in nodes]) - set(['__pycache__'])


def showvirtualenv(env):
    columns, _ = get_terminal_size()
    pkgs = packages(sitepackages_dir(env))
    env_python = workon_home / env / env_bin_dir / 'python'
    l = len(env) + 2
    version = invoke(str(env_python), '-V')
    version = ' - '.join((version.out + version.err).splitlines())
    print(env, ': ', version, sep='')
    print(textwrap.fill(' '.join(pkgs),
                        width=columns-l,
                        initial_indent=(l * ' '),
                        subsequent_indent=(l * ' ')), '\n')


def show_cmd(argv):
    try:
        showvirtualenv(argv[0])
    except IndexError:
        if 'VIRTUAL_ENV' in os.environ:
            showvirtualenv(Path(os.environ['VIRTUAL_ENV']).name)
        else:
            sys.exit('pew show [env]')


def lsenvs():
    return sorted(set(env.parts[-3] for env in
                      workon_home.glob(os.path.join('*', env_bin_dir, 'python*'))))


def lsvirtualenv(verbose):
    envs = lsenvs()

    if not verbose:
        print_virtualenvs(*envs)
    else:
        for env in envs:
            showvirtualenv(env)


def ls_cmd(argv):
    """List available environments."""
    parser = argparse.ArgumentParser()
    p_group = parser.add_mutually_exclusive_group()
    p_group.add_argument('-b', '--brief', action='store_false')
    p_group.add_argument('-l', '--long', action='store_true')
    args = parser.parse_args(argv)
    lsvirtualenv(args.long)


def workon_cmd(argv):
    """List or change working virtual environments."""
    try:
        env = argv[0]
    except IndexError:
        lsvirtualenv(False)
        return

    env_path = workon_home / env
    if not env_path.exists():
        sys.exit("ERROR: Environment '{0}' does not exist. Create it with \
'pew new {0}'.".format(env))
    else:

        # Check if the virtualenv has an associated project directory and in
        # this case, use it as the current working directory.
        project_dir = get_project_dir(env) or os.getcwd()
        shell(env, cwd=project_dir)


def sitepackages_dir(env=os.environ.get('VIRTUAL_ENV')):
    if not env:
        sys.exit('ERROR: no virtualenv active')
    else:
        env_python = workon_home / env / env_bin_dir / 'python'
        return Path(invoke(str(env_python), '-c', 'import distutils; \
print(distutils.sysconfig.get_python_lib())').out)


def add_cmd(argv):
    """Add the specified directories to the Python path for the currently active virtualenv.

This will be done by placing the directory names in a path file named
"virtualenv_path_extensions.pth" inside the virtualenv's site-packages
directory; if this file does not exists, it will be created first.

"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='remove', action='store_true')
    parser.add_argument('dirs', nargs='+')
    args = parser.parse_args(argv)

    extra_paths = sitepackages_dir() / '_virtualenv_path_extensions.pth'
    new_paths = [os.path.abspath(d) + "\n" for d in args.dirs]
    if not extra_paths.exists():
        with extra_paths.open('w') as extra:
            extra.write('''import sys; sys.__plen = len(sys.path)
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


def sitepackages_dir_cmd(argv):
    print(sitepackages_dir())


def lssitepackages_cmd(argv):
    """Show the content of the site-packages directory of the current virtualenv."""
    site = sitepackages_dir()
    print(*site.iterdir())
    extra_paths = site / '_virtualenv_path_extensions.pth'
    if extra_paths.exists():
        print('from _virtualenv_path_extensions.pth:')
        with extra_paths.open() as extra:
            print(''.join(extra.readlines()))


def toggleglobalsitepackages_cmd(argv):
    """Toggle the current virtualenv between having and not having access to the global site-packages."""
    quiet = argv == ['-q']
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


def cp_cmd(argv):
    """Duplicate the named virtualenv to make a new one."""
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('target', nargs='?')
    parser.add_argument('-d', '--dont-activate', action='store_false',
                        default=True, dest='activate', help="After \
                        creation, continue with the existing shell (don't \
                        activate the new environment).")

    args = parser.parse_args(argv)
    target_name = copy_virtualenv_project(args.source, args.target)
    if args.activate:
        shell(target_name)


def copy_virtualenv_project(source, target):
    source = expandpath(source)
    if not source.exists():
        source = workon_home / source
        if not source.exists():
            sys.exit('Please provide a valid virtualenv to copy')

    target_name = target or source.name

    target = workon_home / target_name

    if target.exists():
        sys.exit('%s virtualenv already exists in %s.' % (
            target_name, workon_home
        ))

    print('Copying {0} in {1}'.format(source, target_name))
    clone_virtualenv(str(source), str(target))
    return target_name


def rename_cmd(argv):
    """Rename a virtualenv"""
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('target')
    pargs = parser.parse_args(argv)
    copy_virtualenv_project(pargs.source, pargs.target)
    rmvirtualenvs([pargs.source])


def setvirtualenvproject(env, project):
    print('Setting project for {0} to {1}'.format(env, project))
    with (workon_home / env / '.project').open('wb') as prj:
        prj.write(str(project).encode())


def setproject_cmd(argv):
    """Given a virtualenv directory and a project directory, set the
    virtualenv up to be associated with the project."""
    args = dict(enumerate(argv))
    project = os.path.abspath(args.get(1, '.'))
    env = args.get(0, os.environ.get('VIRTUAL_ENV'))
    if not env:
        sys.exit('pew setproject [virtualenv] [project_path]')
    if not os.path.isdir(project):
        sys.exit('pew setproject: %s does not exist' % project)
    setvirtualenvproject(env, project)


def mkproject_cmd(argv):
    """Create a new project directory and its associated virtualenv."""
    if '-l' in argv or '--list' in argv:
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

    args, rest = parser.parse_known_args(argv)

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


def mktmpenv_cmd(argv):
    """Create a temporary virtualenv."""
    parser = mkvirtualenv_argparser()
    env = '.'
    while (workon_home / env).exists():
        env = hex(random.getrandbits(64))[2:-1]

    args, rest = parser.parse_known_args(argv)

    mkvirtualenv(env, args.python, args.packages, requirements=args.requirements,
                 rest=rest)
    print('This is a temporary environment. It will be deleted when you exit')
    try:
        if args.activate:
            # only used for testing on windows
            shell(env)
    finally:
        rmvirtualenvs([env])


def wipeenv_cmd(argv):
    """Remove all installed packages from the current (or supplied) env."""
    env = argv[0] if argv else os.environ.get('VIRTUAL_ENV')

    if not env:
        sys.exit('ERROR: no virtualenv active')
    elif not (workon_home / env).exists():
        sys.exit("ERROR: Environment '{0}' does not exist.".format(env))
    else:
        env_pip = str(workon_home / env / env_bin_dir / 'pip')
        all_pkgs = set(invoke(env_pip, 'freeze').out.splitlines())
        pkgs = set(p for p in all_pkgs if len(p.split("==")) == 2)
        ignored = sorted(all_pkgs - pkgs)
        pkgs = set(p.split("==")[0] for p in pkgs)
        to_remove = sorted(pkgs - set(['distribute', 'wsgiref']))
        if to_remove:
            print("Ignoring:\n %s" % "\n ".join(ignored))
            print("Uninstalling packages:\n %s" % "\n ".join(to_remove))
            inve(env, 'pip', 'uninstall', '-y', *to_remove)
        else:
            print("Nothing to remove")


def inall_cmd(argv):
    """Run a command in each virtualenv."""
    envs = lsenvs()
    errors = False
    for env in envs:
        print("\n%s:" % env)
        try:
            inve(env, *argv)
        except CalledProcessError as e:
            errors = True
            print(e, file=sys.stderr)
    sys.exit(errors)


def in_cmd(argv):
    """Run a command in the given virtualenv."""

    if len(argv) < 1:
        sys.exit('You must provide a valid virtualenv to target')

    if len(argv) == 1:
        return workon_cmd(argv)

    env = argv[0]
    if not (workon_home / env).exists():
        sys.exit("ERROR: Environment '{0}' does not exist. Create it with \
'pew new {0}'.".format(env))

    inve(*argv)


def restore_cmd(argv):
    """Try to restore a broken virtualenv by reinstalling the same python version on top of it"""

    if len(argv) < 1:
        sys.exit('You must provide a valid virtualenv to target')

    env = argv[0]
    py = workon_home / env / env_bin_dir / ('python.exe' if windows else 'python')
    exact_py = py.resolve().name

    check_call(["virtualenv", env, "--python=%s" % exact_py], cwd=str(workon_home))


def install_cmd(argv):
    '''Use Pythonz to download and build the specified Python version'''
    installer = InstallCommand()
    options, versions = installer.parser.parse_args(argv)
    if len(versions) != 1:
        installer.parser.print_help()
        sys.exit(1)
    else:
        try:
            actual_installer = PythonInstaller.get_installer(versions[0], options)
            actual_installer.install()
        except AlreadyInstalledError as e:
            print(e)


def list_pythons_cmd(argv):
    '''List the pythons installed by Pythonz (or all the installable ones)'''
    ListPythons().run(argv)


def locate_python_cmd(argv):
    '''Locate the path for the python version installed by Pythonz'''
    LocatePython().run(argv)


def version_cmd(argv):
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


def first_run_setup():
    shell = supported_shell()
    if shell:
        if shell == 'fish':
            source_cmd = 'source (pew shell_config)'
        else:
            source_cmd = 'source $(pew shell_config)'
        rcpath = expandpath({'bash': '~/.bashrc'
                           , 'zsh': '~/.zshrc'
                           , 'fish': '~/.config/fish/config.fish'}[shell])
        with rcpath.open('r+') as rcfile:
            if (source_cmd + '\n') not in rcfile.readlines():
                choice = 'X'
                while choice not in ('y', '', 'n'):
                    choice = input("It seems that you're running pew for the first time\n"
                                   "do you want to modify %s to source completions and"
                                   " update your prompt? [y/N]\n> " % rcpath).lower()
                if choice == 'y':
                    rcfile.write('\n# added by Pew\n%s\n' % source_cmd)
                    print('Done')
                else:
                    print('\nOk, if you want to do it manually, just add\n %s\nat'
                          ' the end of %s' % (source_cmd, rcpath))
                print('\nWill now continue with the command:', *sys.argv[1:])
                input('[enter]')


def print_commands(cmds):
    longest = max(map(len, cmds)) + 3
    columns, _ = get_terminal_size()

    print('Available commands:\n')
    for cmd, fun in sorted(cmds.items()):
        if fun.__doc__:
            print(textwrap.fill(
                fun.__doc__.splitlines()[0],
                columns or 1000,
                initial_indent=(' {0}: '.format(cmd)).ljust(longest),
                subsequent_indent=longest * ' '))
        else:
            print(' ' + cmd)


def pew():
    first_run = makedirs_and_symlink_if_needed(workon_home)
    if first_run and sys.stdin.isatty():
        first_run_setup()

    cmds = dict((cmd[:-4], fun)
                for cmd, fun in globals().items() if cmd.endswith('_cmd'))
    if sys.argv[1:]:
        if sys.argv[1] in cmds:
            command = cmds[sys.argv[1]]
            try:
                return command(sys.argv[2:])
            except CalledProcessError as e:
                return e.returncode
            except KeyboardInterrupt:
                pass
        else:
            print("ERROR: command %s does not exist." % sys.argv[1],
                  file=sys.stderr)
            print_commands(cmds)
            sys.exit(1)
    else:
        print_commands(cmds)
