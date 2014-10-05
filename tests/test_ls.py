from pathlib import Path

import pytest

from pew._utils import invoke_pew as invoke

def test_get_site_packages_dir(workon_home):
    d = invoke('new', 'env', inp='pew-sitepackages_dir').out
    assert Path(d).exists
    invoke('rm', 'env')

def test_lssitepackages(workon_home):
    pkgs = invoke('new', 'env', inp="pew lssitepackages").out
    assert 'easy_install' in pkgs
    invoke('rm', 'env')

def test_lssitepackages_add(workon_home):
    invoke('new', 'env', inp="pew add .")
    pkgs = invoke('workon', 'env', inp='pew lssitepackages').out
    assert str(Path('.').absolute()) in pkgs
    invoke('rm', 'env')

