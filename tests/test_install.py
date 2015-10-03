import sys
import os
from subprocess import check_call
from pew._utils import invoke_pew as invoke
from utils import skip_windows
import pytest


@skip_windows(reason='Pythonz is unsupported')
@pytest.mark.skipif(sys.version_info > (2,7) and os.environ.get('CI') == 'true',
                    reason='Limit this slow and expensive test to the oldest '
                    'Python version in the CI environment')
def test_install():
    py_version = ['2.6.1', '--type', 'pypy']
    assert invoke('install', *py_version).returncode == 0
    py = invoke('locate_python', *py_version).out
    check_call([py, '-V'])
