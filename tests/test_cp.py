from sys import platform, executable
from subprocess import check_call
from pathlib import Path

from pew._utils import invoke_pew as invoke
from utils import skip_windows

import pytest

which_cmd = 'where' if platform == 'win32' else 'which'

pytestmark = skip_windows(
    reason='temporarily disable tests, due to issues with the virtualenv-clone'
    ' executable, maybe this bug? http://bugs.python.org/issue20614'
)


@pytest.yield_fixture()
def copied_env(workon_home, env1):
    invoke('cp', 'env1', 'destination', '-d')
    yield workon_home / 'destination'
    invoke('rm', 'destination')


def test_new_env_activated(workon_home, testpackageenv):
    invoke('cp', 'source', 'destination', '-d')
    testscript = Path(invoke('in', 'destination', which_cmd, 'testscript.py').out.strip())
    assert ('destination', 'testscript.py') == (testscript.parts[-3], testscript.parts[-1])
    with testscript.open() as f:
        assert str(workon_home / 'destination') in f.read()
    invoke('rm', 'destination')


def test_virtualenv_variable(copied_env):
    envname = invoke('workon', copied_env.name, inp='echo $VIRTUAL_ENV').out.strip()
    assert str(copied_env) == envname


def test_source_relocatable(workon_home, testpackageenv):
    check_call([executable, '-m', 'virtualenv', '--relocatable',
                str(workon_home / 'source')])
    invoke('cp', 'source', 'destination', '-d')
    testscript = Path(invoke('workon', 'destination', inp='which testscript.py').out.strip())
    assert workon_home / 'destination' / 'bin' / 'testscript.py' == testscript
    invoke('rm', 'destination')


def test_source_does_not_exists(workon_home):
    err = invoke('cp', 'virtualenvthatdoesntexist', 'foo').err.strip()
    assert 'Please provide a valid virtualenv to copy' == err
    invoke('rm', 'destination')


def test_no_global_site_packages(copied_env):
    site = Path(invoke('workon', copied_env.name, inp='pew sitepackages_dir').out)
    assert (site.parent / 'no-global-site-packages.txt').exists
