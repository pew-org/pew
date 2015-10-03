from pew._utils import invoke_pew as invoke
from subprocess import check_call


def test_install():
    py_version = ['2.6.1', '--type', 'pypy']
    assert invoke('install', *py_version).returncode == 0
    py = invoke('locate_python', *py_version).out
    check_call([py, '-V'])
