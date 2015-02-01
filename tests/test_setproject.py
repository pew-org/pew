from pew._utils import invoke_pew as invoke
import tempfile
import os
import shutil
import pytest


def test_project_dont_exist(env1):
    out = invoke('setproject', 'env1', 'i/dont/exist')
    assert out.err


@pytest.yield_fixture()
def tmp_cwd():
    tmpdir = tempfile.mkdtemp()
    old_cwd = os.getcwd()
    os.chdir(tmpdir)
    yield
    os.chdir(old_cwd)
    shutil.rmtree(tmpdir)


def test_project_exist(env1, tmp_cwd):
    tmpdir = tempfile.mkdtemp()
    out = invoke('setproject', 'env1', tmpdir)
    assert not out.err
    shutil.rmtree(tmpdir)


def test_workon_when_project_is_relative(env1, tmp_cwd):
    os.mkdir('i_exist')
    out = invoke('setproject', 'env1', 'i_exist')
    os.mkdir('elsewhere')
    os.chdir('elsewhere')
    out = invoke('workon', 'env1')
    assert not out.out
    assert (
        out.err == "Launching subshell in virtual environment. Type 'exit' or "
                   "'Ctrl+D' to return."
    )
    os.chdir('..')
    shutil.rmtree('i_exist')
