from sys import platform
from subprocess import check_call, CalledProcessError
from pathlib import Path

import pytest

from pew._utils import invoke_pew as invoke

windows = platform == 'win32'

skip_windows = pytest.mark.skipif(windows, reason='cannot supply stdin to powershell')


@skip_windows
def test_mktmpenv(workon_home):
    envs = set(invoke('ls').out.split())
    envs2 = set(invoke('mktmpenv', inp='pew ls').out.split())
    assert envs < envs2


def test_mktmpenv_extra_name(workon_home):
    with pytest.raises(CalledProcessError):
        check_call('pew mktmpenv yada'.split())


@skip_windows
def test_mktmpenv_ngsp(workon_home):
    site = Path(invoke('mktmpenv', inp='pew sitepackages_dir').out)
    assert (site.parent / 'no-global-site-packages.txt').exists


def test_mktmpenv_autodeletes(workon_home):
    envs = set(invoke('ls').out.split())
    invoke('mktmpenv', '-d' if platform == 'win32' else '')
    envs2 = set(invoke('ls').out.split())
    assert envs == envs2

@skip_windows
def test_mktmpenv_workon_alt(workon_alt):
    out = invoke('mktmpenv', '-w', str(workon_alt), inp="python -c 'import os; print(os.environ[\'WORKON_HOME\'])").out
    assert str(workon_alt) in out