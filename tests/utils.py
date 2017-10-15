try:
    from tempfile import TemporaryDirectory
except ImportError:
    from shutil import rmtree
    from contextlib import contextmanager
    from tempfile import mkdtemp

    @contextmanager
    def TemporaryDirectory():
        tmpdir = mkdtemp()
        yield tmpdir
        rmtree(tmpdir)

import functools
import os
from sys import platform

import pytest

skip_windows = functools.partial(pytest.mark.skipif, platform == 'win32')
xfail_nix = pytest.mark.xfail(os.environ.get('NIX'),
                              reason="Test not yet working while building in Nix")