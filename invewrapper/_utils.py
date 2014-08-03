import os
import sys
import locale
import contextlib
from subprocess import check_call, call

try:
    from subprocess import check_output
except ImportError:
    from subprocess import Popen, PIPE  # py2.6 compatibility

    def check_output(cmd, *args, **kwargs):
        popen = Popen(cmd, *args, stdout=PIPE, **kwargs)
        output = popen.communicate()[0]
        return_code = popen.poll()
        if return_code:
            raise Exception('Command %r failed with return code %r' % (
                cmd, return_code))
        return output


locale.setlocale(locale.LC_ALL, '')


def which(fn):
    """Simplified version of shutil.which for internal usage.

Doesn't look up commands ending in '.exe' (we don't use them),
nor does it avoid looking up commands that already have their directory
specified (we don't use them either) and it doesn't check the current directory,
just like on *nix systems.
"""

    def _access_check(fn):
        return (os.path.exists(fn) and os.access(fn, os.F_OK | os.X_OK)
                and not os.path.isdir(fn))
    pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
    files = [fn + ext.lower() for ext in pathext]
    path = os.environ.get("PATH", os.defpath).split(os.pathsep)
    seen = set()
    for dir in map(os.path.normcase, path):
        if dir not in seen:
            seen.add(dir)
            for name in map(lambda f: os.path.join(dir, f), files):
                if _access_check(name):
                    return name


def check_path():
    parent = os.path.dirname
    return parent(parent(which('python'))) == os.environ['VIRTUAL_ENV']


def resolve_path(f):
    if sys.platform != 'win32':
        return f
    else:
        def call(cmd, *args):
            ex = cmd[0]
            ex = which(ex) or ex
            return f([ex] + cmd[1:], *args)
        return call

check_output = resolve_path(check_output)
check_call = resolve_path(check_call)
call = resolve_path(call)


def shell(*args):
    return check_output(*args).decode(locale.getlocale()[1]).strip()

env_bin_dir = 'bin'
if sys.platform == 'win32':
    env_bin_dir = 'Scripts'


def expandpath(path):
    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))


def own(path):
    if sys.platform == 'win32':
        # Even if run by an administrator, the permissions will be set
        # correctly on Windows, no need to check
        return True
    while not os.path.exists(path):
        path = os.path.dirname(path)
    return os.stat(path).st_uid == os.getuid()


@contextlib.contextmanager
def chdir(dirname):
    curdir = os.getcwd()
    try:
        os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)
