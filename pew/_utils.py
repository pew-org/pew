import os
import sys
import locale
from contextlib import contextmanager
from subprocess import check_call, Popen, PIPE
from collections import namedtuple
from functools import partial
from pathlib import Path

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
        def call(cmd, **kwargs):
            ex = cmd[0]
            ex = which(ex) or ex
            return f([ex] + list(cmd[1:]), **kwargs)
        return call

check_call = resolve_path(check_call)
Popen = resolve_path(Popen)

Result = namedtuple('Result', 'out err')

# TODO: it's better to fail early, and thus I'd need to check the exit code, but it'll
# need a refactoring of a couple of tests
def invoke(*args, **kwargs):
    encoding = locale.getlocale()[1]
    inp = kwargs.pop('inp', '').encode(encoding)
    popen = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, **kwargs)
    return Result(*[o.strip().decode(encoding) for o in popen.communicate(inp)])


invoke_pew = partial(invoke, 'pew')

env_bin_dir = 'bin' if sys.platform != 'win32' else 'Scripts'


def expandpath(path):
    return Path(os.path.expanduser(os.path.expandvars(path)))


def own(path):
    if sys.platform == 'win32':
        # Even if run by an administrator, the permissions will be set
        # correctly on Windows, no need to check
        return True
    while not path.exists():
        path = path.parent
    return path.stat().st_uid == os.getuid()


@contextmanager
def temp_environ():
    environ = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(environ)
