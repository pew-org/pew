from subprocess import check_call, CalledProcessError
from pathlib import Path

import pytest

from pew._utils import invoke_pew as invoke


def test_mktmpenv(workon_home):
    envs = set(invoke('ls').out.split())
    envs2 = set(invoke('mktmpenv', inp='pew ls').out.split())
    assert envs < envs2


def test_mktmpenv_extra_name(workon_home):
    with pytest.raises(CalledProcessError):
        check_call('pew mktmpenv yada'.split())


def test_mktmpenv_ngsp(workon_home):
    site = Path(invoke('mktmpenv', inp='pew sitepackages_dir').out)
    assert (site.parent / 'no-global-site-packages.txt').exists


def test_mktmpenv_autodeletes(workon_home):
    envs = set(invoke('ls').out.split())
    invoke('mktmpenv', '-d')
    envs2 = set(invoke('ls').out.split())
    assert envs == envs2
