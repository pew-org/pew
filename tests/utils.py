from tempfile import TemporaryDirectory

from urllib.request import urlopen
from urllib.error import URLError


import functools
import os
from sys import platform

import pytest

skip_windows = functools.partial(pytest.mark.skipif, platform == 'win32')

def are_we_connected():
    try:
        urlopen('http://google.com')
        return True
    except URLError:
        return False


connection_required = pytest.mark.skipif(not are_we_connected(),
                                         reason="An internet connection is required")
