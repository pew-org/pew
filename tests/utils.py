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

try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib import urlopen
    URLError = IOError


import functools
import sys

import pytest

from pew._utils import uses_venv

skip_windows = functools.partial(pytest.mark.skipif, sys.platform == 'win32')


skip_venv = functools.partial(pytest.mark.skipif, uses_venv())

skip_venv_site_packages = functools.partial(
    pytest.mark.skipif, uses_venv(),
    reason='TODO: Add a similar test for pyvenv.cfg',
)


def are_we_connected():
    try:
        urlopen('http://google.com')
        return True
    except URLError:
        return False


connection_required = pytest.mark.skipif(
    not are_we_connected(),
    reason="An internet connection is required",
)
