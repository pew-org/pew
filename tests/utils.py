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
import os
from sys import platform, version_info

import pytest

skip_windows = functools.partial(pytest.mark.skipif, platform == 'win32')


def use_venv():
    return (
        platform != 'win32' and
        version_info >= (3, 4) and
        not os.environ.get('PEW_USE_VIRTUALENV')
    )


skip_venv = functools.partial(pytest.mark.skipif, use_venv())

skip_venv_site_packages = functools.partial(
    pytest.mark.skipif, use_venv(),
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
