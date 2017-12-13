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
except ImportError:
    from urllib2 import urlopen

import functools
import os
from sys import platform

import pytest


def has_connection():
    try:
        urlopen('https://pypi.org/')
    except OSError:
        return False
    return True


skip_windows = functools.partial(pytest.mark.skipif, platform == 'win32')
xfail_nix = pytest.mark.xfail(os.environ.get('NIX'),
                              reason="Test not yet working while building in Nix")
skip_webtest = pytest.mark.skipif(has_connection() is False,
                                  reason="Test requires an internet connection")
