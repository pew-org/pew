#! /usr/bin/env python

from __future__ import print_function, absolute_import

import os
import sys
import argparse
import shutil
import random
import textwrap
from glob import glob
from subprocess import CalledProcessError

try:
    from clonevirtualenv import clone_virtualenv
except ImportError:
    pass # setup.py needs to import this before the dependencies are installed

from pew._utils import (call, check_call, shell, chdir, expandpath, own,
                        env_bin_dir, check_path)


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
    if not os.path.exists(workon_home) and own(workon_home):
        os.makedirs(workon_home)
        if os.name == 'posix' and 'WORKON_HOME' not in os.environ and \
           'XDG_DATA_HOME' not in os.environ:
            os.symlink(workon_home, expandpath('~/.virtualenvs'))

makedirs_and_symlink_if_needed(workon_home)


inve_site = os.path.dirname(__file__)
source_inve = os.path.join(inve_site, 'inve')


def deploy_completions():
    completions = {'complete.bash': '/etc/bash_completion.d/pew',
                   'complete.zsh': '/usr/local/share/zsh/site-functions/_pew',
                   'complete.fish': '/etc/fish/completions/pew.fish'}
    for comp, dest in completions.items():
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        shutil.copy(os.path.join(inve_site, 'complete_scripts', comp), dest)


def get_inve(env):
    return os.path.join(workon_home, env, env_bin_dir, 'inve')


def get_project_dir(env):
    project_dir = None
    project_file = os.path.join(workon_home, env, '.project')
    if os.path.exists(project_file):
        with open(project_file, 'r') as f:
            project_dir = f.readline().strip()

    return project_dir


def invoke(inve, *args):
    windows = sys.platform == 'win32'
    if not args:
        args = ['powershell' if windows else os.environ['SHELL']]
        if not windows:
            # On Windows the PATH is usually set with System Utility
            # so we won't worry about trying to check mistakes there
            shell_check = [sys.executable + ' -c "from pew.pew import '
                           'prevent_path_errors; prevent_path_errors()"']
            if call(['python', inve, args[0], '-c'] + shell_check) != 0:
                return
        or_ctrld = '' if windows else "or 'Ctrl+D' "
        sys.stderr.write("Launching subshell in virtual environment. Type "
                         "'exit' %sto return.\n" % or_ctrld)

    check_call(['python', inve] + list(args))


def deploy_inve(target):
    # temporary workaround: I plan to remove it when virtualenv's PR #247
    # will be completed
    shutil.copy(source_inve, target)


def mkvirtualenv(envname, python=None, packages=[], project=None,
                 requirements=None, rest=[]):

    if python:
        rest = ["--python=%s" % python] + rest

    try:
        with chdir(workon_home):
            check_call(["virtualenv", envname] + rest)

            if project:
                setvirtualenvproject(envname, project)

        inve = get_inve(envname)
        deploy_inve(inve)

        if requirements:
            invoke(inve, 'pip', 'install', '--allow-all-external', '-r', expandpath(requirements))

        if packages:
            invoke(inve, 'pip', 'install', '--allow-all-external', *packages)

        return inve
    except CalledProcessError:
        rmvirtualenvs([envname])
        raise


def mkvirtualenv_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--python')
    parser.add_argument('-i', action='append', dest='packages', help='Install \
a package after the environment is created. This option may be repeated.')
    parser.add_argument('-a', dest='project', help='Provide a full path to a \
project directory to associate with the new environment.')
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
    parser.add_argument('envname')
    args, rest = parser.parse_known_args()

    inve = mkvirtualenv(args.envname, args.python, args.packages, args.project,
                        args.requirements, rest)
    if args.activate:
        invoke(inve)


def rmvirtualenvs(envs):
    with chdir(workon_home):
        for env in envs:
            env = os.path.join(workon_home, env)
            if os.environ.get('VIRTUAL_ENV') == env:
                print("ERROR: You cannot remove the active environment \
(%s)." % env, file=sys.stderr)
                break
            try:
                shutil.rmtree(env)
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
            showvirtualenv(os.path.basename(os.environ['VIRTUAL_ENV']))
        else:
            sys.exit('pew-show [env]')


def lsvirtualenv(verbose):
    envs = sorted(set(env.split(os.path.sep)[-3] for env in
                      glob(os.path.join(workon_home, '*', env_bin_dir, 'python*'))))
    for env in envs:
        deploy_inve(get_inve(env))

    if not verbose:
        print(' '.join(envs))
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

    env_path = os.path.join(workon_home, env)
    if not os.path.exists(env_path):
        sys.exit("ERROR: Environment '{0}' does not exist. Create it with \
'pew-new {0}'.".format(env))
    else:

        # Check if the virtualenv has an associated project directory and in
        # this case, use it as the current working directory.
        project_dir = get_project_dir(env) or os.getcwd()
        with chdir(project_dir):
            inve = get_inve(env)
            deploy_inve(inve)
            invoke(inve)


def sitepackages_dir():
    if 'VIRTUAL_ENV' not in os.environ:
        sys.exit('ERROR: no virtualenv active')
    else:
        return shell(['python', '-c', 'import distutils; \
print(distutils.sysconfig.get_python_lib())'])


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

    extra_paths = os.path.join(sitepackages_dir(), '_virtualenv_path_extensions.pth')
    new_paths = [os.path.abspath(d) + "\n" for d in args.dirs]
    if not os.path.exists(extra_paths):
        with open(extra_paths, 'w') as extra:
            extra.write('''import sys; sys.__plen = len(sys.path)
import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)
''')

    def rewrite(f):
        with open(extra_paths, 'r+') as extra:
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
    print(*os.listdir(site))
    extra_paths = os.path.join(site, '_virtualenv_path_extensions.pth')
    if os.path.exists(extra_paths):
        print('from _virtualenv_path_extensions.pth:')
        with open(extra_paths) as extra:
            print(''.join(extra.readlines()))


def toggleglobalsitepackages_cmd():
    """Toggle the current virtualenv between having and not having access to the global site-packages."""
    quiet = args.get(1) == '-q'
    site = sitepackages_dir()
    ngsp_file = os.path.join(os.path.dirname(site),
                             'no-global-site-packages.txt')
    if os.path.exists(ngsp_file):
        os.remove(ngsp_file)
        if not quiet:
            print('Enabled global site-packages')
    else:
        with open(ngsp_file, 'w'):
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
    source_name = sys.argv[1]
    if os.path.exists(args.source):
        source = expandpath(args.source)
    else:
        source = expandpath(os.path.join(workon_home, args.source))
        if not os.path.exists(source):
            sys.exit('Please provide a valid virtualenv to copy')

    target_name = args.target or os.path.basename(source)

    target = os.path.join(workon_home, target_name)

    if os.path.exists(target):
        sys.exit('%s virtualenv already exists in %s.' % (target_name, workon_home))

    print('Copying {0} in {1}'.format(source, target_name))
    clone_virtualenv(source, target)
    inve = get_inve(target_name)
    deploy_inve(inve)
    if args.activate:
        invoke(inve)


def setvirtualenvproject(env, project):
    print('Setting project for {0} to {1}'.format(os.path.basename(env),
                                                  project))
    with open(os.path.join(env, '.project'), 'w') as prj:
        prj.write(project)


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
        templates = [t.split(os.path.sep)[-1][9:] for t in
                     glob(os.path.join(workon_home, "template_*"))]
        print("Available project templates:\n%s" % "\n".join(templates))
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

    projects_home = os.environ.get('PROJECT_HOME', '.')
    if not os.path.exists(projects_home):
        sys.exit('ERROR: Projects directory %s does not exist. \
Create it or set PROJECT_HOME to an existing directory.' % projects_home)

    project = os.path.abspath(os.path.join(projects_home, args.envname))
    if os.path.exists(project):
        sys.exit('Project %s already exists.' % args.envname)

    inve = mkvirtualenv(args.envname, args.python, args.packages, args.project,
                        args.requirements, rest)

    os.mkdir(project)

    setvirtualenvproject(os.path.join(workon_home, args.envname), project)

    with chdir(project):
        for template_name in args.templates:
            template = os.path.join(workon_home, "template_" + template_name)
            invoke(inve, template, args.envname, project)
        if args.activate:
            invoke(inve)


def mktmpenv_cmd():
    """Create a temporary virtualenv."""
    parser = mkvirtualenv_argparser()
    env = '.'
    while os.path.exists(os.path.join(workon_home, env)):
        env = hex(random.getrandbits(64))[2:-1]

    args, rest = parser.parse_known_args()

    inve = mkvirtualenv(env, args.python, args.packages, args.project,
                        args.requirements, rest)
    print('This is a temporary environment. It will be deleted when you exit')
    try:
        invoke(inve)
    finally:
        rmvirtualenvs([env])


def wipeenv_cmd():
    """Remove all installed packages from the current env."""
    pkgs = map(lambda d: d.split("==")[0], shell(['pip', 'freeze']).split())
    to_remove = [pkg for pkg in pkgs if pkg not in ('distribute', 'wsgiref')]
    if to_remove:
        print("Uninstalling packages:\n%s" % "\n".join(to_remove))
        check_call(['pip', 'uninstall', '-y'] + to_remove)
    else:
        print("Nothing to remove")


def inall_cmd():
    """Run a command in each virtualenv."""
    inves = glob(os.path.join(workon_home, '*', env_bin_dir, 'inve'))
    for inve in inves:
        print("\n%s:" % inve.split(os.path.sep)[-3])
        invoke(inve, *sys.argv[1:])


def in_cmd():
    """Run a command in the given virtualenv."""

    if len(sys.argv) < 2:
        sys.exit('You must provide a valid virtualenv to target')

    env = sys.argv[1]
    env_path = os.path.join(workon_home, env)
    if not os.path.exists(env_path):
        sys.exit("ERROR: Environment '{0}' does not exist. Create it with \
'pew-new {0}'.".format(env))

    inve = get_inve(env)
    deploy_inve(inve)
    invoke(inve, *sys.argv[2:])

def restore_cmd():
    """Try to restore a broken virtualenv by reinstalling the same python
version on top of it"""

    if len(sys.argv) < 2:
        sys.exit('You must provide a valid virtualenv to target')

    env = sys.argv[1]
    py = os.path.join(workon_home, env, env_bin_dir, 'python')
    exact_py = os.path.basename(os.readlink(py))

    with chdir(workon_home):
        check_call(["virtualenv", env, "--python=%s" % exact_py])


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
