import functools
import pytest

from sys import platform


skip_windows = functools.partial(pytest.mark.skipif, platform == 'win32')
