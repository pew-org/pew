from os import unlink
from subprocess import check_call, CalledProcessError
from pathlib import Path
from tempfile import NamedTemporaryFile
try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib import urlopen
    URLError = IOError

import pytest

from pew._utils import invoke_pew as invoke


def are_we_connected():
    try:
        urlopen('http://google.com')
        return True
    except URLError:
        return False


connection_required = pytest.mark.skipif(
    not are_we_connected(), reason="An internet connection is required"
)


def test_create(workon_home):
    envs = set(invoke('ls').out.split())
    invoke('new', 'env', '-d')
    envs2 = set(invoke('in', 'env', 'pew', 'ls').out.split())
    invoke('rm', 'env')
    assert envs < envs2


def test_no_args(workon_home):
    with pytest.raises(CalledProcessError):
        check_call(['pew', 'new'])


def test_gsp(workon_home):
    invoke('new', 'env', '--system-site-packages', '-d')
    site = invoke('in', 'env', 'pew', 'sitepackages_dir').out
    assert not (Path(site).parent / 'no-global-site-packages.txt').exists()
    invoke('rm', 'env')


def test_associate(workon_home):
    project = Path('/dev/null')
    invoke('new', 'env', '-a', str(project), '-d')
    dotproject = workon_home / 'env' / '.project'
    assert dotproject.exists()
    with dotproject.open() as f:
        assert f.read() == str(project.absolute())
    invoke('rm', 'env')


@connection_required
def test_install_pkg(workon_home):
    invoke('new', 'env', '-i', 'IPy', '-d')
    freeze = invoke('in', 'env', 'pip', 'freeze').out
    assert 'IPy' in freeze
    invoke('rm', 'env')


@connection_required
def test_install_2pkgs(workon_home):
    invoke('new', 'env', '-i', 'IPy', '-i', 'WebTest', '-d')
    freeze = invoke('in', 'env', 'pip', 'freeze').out
    assert 'IPy' in freeze
    assert 'WebTest' in freeze
    invoke('rm', 'env')


@connection_required
def test_requirements_file(workon_home):
    with NamedTemporaryFile(delete=False) as temp:
        temp.write(b'IPy')
        temp.close()
        invoke('new', 'env', '-r', temp.name, '-d')
        freeze = invoke('in', 'env', 'pip', 'freeze').out
        assert 'IPy' in freeze
        invoke('rm', 'env')
        unlink(temp.name)
