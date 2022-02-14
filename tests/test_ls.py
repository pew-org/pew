from pathlib import Path
import re

from pew._utils import invoke_pew as invoke


def test_ls(workon_home):
    r = invoke('ls')
    assert not r.out and not r.err

def test_get_site_packages_dir(workon_home):
    invoke('new', 'env', '-d')
    d = invoke('in', 'env', 'pew', 'sitepackages_dir').out
    assert Path(d).exists
    invoke('rm', 'env')


def test_lssitepackages(workon_home):
    invoke('new', 'env', '-d')
    pkgs = invoke('in', 'env', 'pew', 'lssitepackages').out
    assert re.search(r'setuptools-((\d+\.)+)dist-info', pkgs)
    invoke('rm', 'env')


def test_lssitepackages_add(workon_home):
    invoke('new', 'env', '-d')
    invoke('in', 'env', 'pew', 'add', '.')
    pkgs = invoke('in', 'env', 'pew', 'lssitepackages').out
    assert str(Path('.').absolute()) in pkgs
    invoke('rm', 'env')
