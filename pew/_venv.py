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
    def create_env(self, args):
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


class VenvBackend(Backend):
    """Functionality provided by venv, built-in since Python 3.4.
    """
    module_name = 'venv'

    def create_env(self, args):
        # We need to run venv on the Python we want to use. sys.executable is
        # not enough because it might come from a venv itself. venv can be
        # easily confused if it is nested inside another venv.
        # https://bugs.python.org/issue30811
        import sysconfig
        py = pathlib.Path(
            sysconfig.get_config_var('BINDIR'),
            ('python.exe' if windows else 'python'),
        )
        subprocess.check_call([str(py), '-m', 'venv', str(self.root)] + args)

    def restore_env(self):
        cfg = Cfg(self.root.joinpath('pyvenv.cfg'))
        py = pathlib.Path(cfg.bindir, ('python.exe' if windows else 'python'))
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

    # A bug is preventing the venv to be usable on Windows. Disabling for now.
    # https://bugs.python.org/issue30811
    if windows:
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
