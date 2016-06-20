import tempfile
import os
import shutil
from pathlib import Path

import pytest

from pew._utils import temp_environ, invoke_pew as invoke
from utils import skip_windows, TemporaryDirectory


def test_project_dont_exist(env1):
    out = invoke('setproject', 'env1', 'i/dont/exist')
    assert out.err


def check_project_dir(workon_home, env, projdir):
    return (workon_home / env / '.project').open().read() == projdir


@skip_windows(reason="empty stdin on windows doesn't close the subprocess used by workon")
def test_implicit(workon_home, env1):
    "use the current virtualenv to associate the cwd as project directory"
    with TemporaryDirectory() as tmpdir:
        res = invoke('workon', 'env1', inp='pew setproject', cwd=tmpdir)
        assert check_project_dir(workon_home, 'env1', tmpdir)


def test_implicit_project(workon_home, env1):
    "use the cwd as project directory"
    with temp_environ():
        del os.environ['VIRTUAL_ENV']
        with TemporaryDirectory() as tmpdir:
            res = invoke('setproject', 'env1', cwd=tmpdir)
            assert not res.err
            assert check_project_dir(workon_home, 'env1', tmpdir)


def test_setproject(workon_home, env1):
    with temp_environ():
        del os.environ['VIRTUAL_ENV']
        with TemporaryDirectory() as tmpdir:
            res = invoke('setproject', 'env1', tmpdir)
            assert not res.err
            assert check_project_dir(workon_home, 'env1', tmpdir)


@skip_windows(reason="empty stdin on windows doesn't close the subprocess used by workon")
def test_ignore_environ(workon_home, env1, env2):
    with temp_environ():
        del os.environ['VIRTUAL_ENV']
        with TemporaryDirectory() as tmpdir:
            res = invoke('workon', 'env1', inp='pew setproject env2 ' + tmpdir)
            assert not (workon_home / 'env1' / '.project').exists()
            assert check_project_dir(workon_home, 'env2', tmpdir)


@skip_windows(reason="empty stdin on windows doesn't close the subprocess used by workon")
def test_workon_when_project_is_relative(env1):
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        invoke('setproject', 'env1', tmpdir.name, cwd=str(tmpdir.parent))
        workon_projdir = invoke('workon', 'env1', inp='pwd').out.strip()
        assert workon_projdir == str(tmpdir)
