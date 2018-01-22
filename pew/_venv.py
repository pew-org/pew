__all__ = ['choose_backend', 'guess_backend']

import os
import pathlib
import subprocess
import sys
import warnings

from ._cfg import Cfg
from ._utils import env_bin_dir, invoke, windows


class Backend(object):

    def __init__(self, root):
        super(Backend, self).__init__()
        self.root = root.absolute()

    def get_python(self):
        return self.root.joinpath(env_bin_dir, 'python.exe' if windows else 'python')

    def get_sitepackages_dir(self):
        result = invoke(
            str(self.get_python()), '-c',
            'import distutils.sysconfig; '
            'print(distutils.sysconfig.get_python_lib())',
        )
        if result.returncode != 0:
            raise RuntimeError(
                'could not get site-packages location.\n%s' % result.err,
            )
        return pathlib.Path(result.out)


class VirtualenvBackend(Backend):
    """Functionality provided by virtualenv.
    """
    def create_env(self, py, args):
        if py:
            args = ["--python=%s" % py] + args
        subprocess.check_call(
            [sys.executable, '-m', 'virtualenv', str(self.root)] + args,
        )

    def restore_env(self):
        subprocess.check_call([
            sys.executable, "-m", 'virtualenv', str(self.root),
            "--python=%s" % self.get_python().name,
        ])

    def toggle_global_sitepackages(self):
        ngsp = self.get_sitepackages_dir().with_name(
            'no-global-site-packages.txt',
        )
        should_enable = not ngsp.exists()
        if should_enable:
            with ngsp.open('w'):
                pass
        else:
            ngsp.unlink()
        return should_enable


class BrokenEnvironmentError(RuntimeError):
    pass


def find_real_python():
    # We need to run venv on the Python we want to use. sys.executable is not
    # enough because it might come from a venv itself. venv can be easily
    # confused if it is nested inside another venv.
    # https://bugs.python.org/issue30811
    python = ('python.exe' if windows else 'python')

    # If we're in a venv, excellent! The config file has this information.
    pyvenv_cfg = pathlib.Path(sys.prefix, 'pyvenv.cfg')
    if pyvenv_cfg.exists():
        return Cfg(pyvenv_cfg).bindir.joinpath(python)

    # Or we can try looking this up from the build configuration. This is
    # usually good enough, unless we're in a virtualenv (i.e. sys.real_prefix
    # is set), and sysconfig reports the wrong Python (i.e. in the virtualenv).
    import sysconfig
    bindir = sysconfig.get_config_var('BINDIR')
    try:
        real_prefix = sys.real_prefix
    except AttributeError:
        return pathlib.Path(bindir, python)
    if not os.path.realpath(bindir).startswith(real_prefix):
        return pathlib.Path(bindir, python)

    # OK, so we're in a virtualenv, and sysconfig lied. At this point there's
    # no definitive way to tell where the real Python is, so let's make an
    # educated guess. This works if the user isn't using a very exotic build.
    for rel in ['', os.path.relpath(str(bindir), real_prefix), env_bin_dir]:
        try:
            path = pathlib.Path(real_prefix, rel, python).resolve()
        except FileNotFoundError:
            continue
        if path.exists():   # On 3.6+ resolve() doesn't check for existence.
            return path

    # We've tried everything. Sorry.
    raise BrokenEnvironmentError


class VenvBackend(Backend):
    """Functionality provided by venv, built-in since Python 3.4.
    """
    module_name = 'venv'

    def create_env(self, py, args):
        if not py:
            py = find_real_python()
        subprocess.check_call([str(py), '-m', 'venv', str(self.root)] + args)

    def restore_env(self):
        cfg = Cfg(self.root.joinpath('pyvenv.cfg'))
        py = cfg.bindir.joinpath('python.exe' if windows else 'python')
        subprocess.check_call([str(py), "-m", 'venv', str(self.root)])

    def toggle_global_sitepackages(self):
        cfg = Cfg(self.root.joinpath('pyvenv.cfg'))
        should_enable = not cfg.include_system_sitepackages
        cfg.include_system_sitepackages = should_enable
        cfg.save()
        return should_enable


def choose_backend(root):
    """Choose a preferred virtual environment backend to use.
    """
    if sys.version_info < (3, 4) or os.environ.get('PEW_USE_VIRTUALENV'):
        return VirtualenvBackend(root)

    # Without ensurepip the venv can can't bootstrap Setuptools and Pip.
    # That would not be useful for us.
    for module_name in ['ensurepip', 'venv']:
        try:
            __import__(module_name)
        except ImportError:
            warnings.warn(
                'Module "%s" unavailable, falling back to virtualenv...\n'
                'Set PEW_USE_VIRTUALENV environment variable to '
                'suppress this.' % module_name,
                FutureWarning,
            )
            return VirtualenvBackend(root)
    return VenvBackend(root)


def guess_backend(root):
    """Guess what backend a virtual environment backend uses.

    The built-in venv writes a pyvenv.cfg file; check if it exists.
    """
    pyvenv_cfg = root / 'pyvenv.cfg'
    if pyvenv_cfg.exists():
        return VenvBackend(root)
    return VirtualenvBackend(root)
