import sys
import os
from subprocess import check_call
from pew._utils import invoke_pew as invoke
from utils import skip_windows
import pytest

def skip_marker(f):
    return skip_windows(reason='Pythonz unavailable in Windows')(
        pytest.mark.skipif(
            sys.platform == 'cygwin',
            reason='Pythonz unavailable in Cygwin')(
                pytest.mark.skipif(os.environ.get('NIX'),
                                   reason='Pythonz unavailable in Nix')(f)))

@skip_marker
def test_install():
    py_version = ['2.6.1', '--type', 'pypy']
    assert invoke('install', *py_version).returncode == 0
    py = invoke('locate_python', *py_version).out
    check_call([py, '-V'])

@skip_marker
def test_uninstall():
    py_version = ['2.6.1', '--type', 'pypy']
    invoke('install', *py_version)
    assert invoke('uninstall', *py_version).returncode == 0
    assert invoke('locate_python', *py_version).returncode != 0
