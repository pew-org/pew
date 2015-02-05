from pathlib import Path

from pew._utils import invoke_pew as invoke


def test_get_site_packages_dir(workon_home):
    invoke('new', 'env', '-d')
    d = invoke('in', 'env', 'pew-sitepackages_dir').out
    assert Path(d).exists
    invoke('rm', 'env')


def test_lssitepackages(workon_home):
    invoke('new', 'env', '-d')
    pkgs = invoke('in', 'env', 'pew', 'lssitepackages').out
    assert 'easy_install' in pkgs
    invoke('rm', 'env')


def test_lssitepackages_add(workon_home):
    invoke('new', 'env', '-d')
    invoke('in', 'env', 'pew', 'add', '.')
    pkgs = invoke('in', 'env', 'pew', 'lssitepackages').out
    assert str(Path('.').absolute()) in pkgs
    invoke('rm', 'env')


def test_ls_alt(workon_alt):
    invoke('new','alt','-w',str(workon_alt))
    envs = invoke('ls','-w',str(workon_alt)).out
    assert 'alt' in envs
    invoke('rm','alt','-w',str(workon_alt))

