import os
from shutil import rmtree, copy
from tempfile import gettempdir
from pathlib import Path

import pytest

from pew._utils import invoke_pew as invoke


@pytest.yield_fixture(scope='session')
def workon_home():
    tmpdir = os.environ.get('TMPDIR', gettempdir())
    os.environ['WORKON_HOME'] = str(Path(tmpdir) / 'WORKON_HOME')

    workon = Path(os.environ['WORKON_HOME'])
    rmtree(str(workon), ignore_errors=True)
    workon.mkdir(parents=True)
    yield workon
    rmtree(str(workon))


@pytest.yield_fixture()
def workon_sym_home():
    # workon_home() fixture assumes it is the only one changing the environ
    # so save it and restore it after the test
    old_workon = os.environ.get('WORKON_HOME', '')

    tmpdir = os.environ.get('TMPDIR', gettempdir())
    tmpdir = Path(tmpdir) / 'pew-test-tmp'

    # Create the real root and a symlink to it: SYM_ROOT -> REAL_ROOT
    real_root = tmpdir / 'REAL_ROOT'
    sym_root = tmpdir / 'SYM_ROOT'

    real_home = real_root / 'WORKON_HOME'
    real_home.mkdir(parents=True)

    sym_root.symlink_to(real_root, target_is_directory=True)
    sym_home = sym_root / 'WORKON_HOME'

    # New WORKON_HOME lives in the symlinked root
    os.environ['WORKON_HOME'] = str(sym_home)

    workon = Path(os.environ['WORKON_HOME'])
    yield workon
    rmtree(str(tmpdir))
    os.environ['WORKON_HOME'] = old_workon


@pytest.yield_fixture()
def env1(workon_home):
    result = invoke('new', 'env1', '-d')
    assert result.returncode == 0, result.err
    yield
    invoke('rm', 'env1')


@pytest.yield_fixture()
def env2(workon_home):
    result = invoke('new', 'env2', '-d')
    assert result.returncode == 0, result.err
    yield
    invoke('rm', 'env2')


@pytest.yield_fixture()
def testpackageenv(workon_home):
    testpackage = str(Path(__file__).parent / 'testpackage')
    result = invoke('new', 'source', '-d')
    assert result.returncode == 0, result.err
    result = invoke('in', 'source', 'python', 'setup.py', 'install', cwd=testpackage)
    assert result.returncode == 0, result.err
    yield
    invoke('rm', 'source')


@pytest.yield_fixture()
def testtemplate(workon_home):
    sourcetemplate = Path(__file__).parent / 'template_test'
    testtemplatefile = workon_home / 'template_test'
    copy(str(sourcetemplate), str(testtemplatefile))
    testtemplatefile.chmod(0o700)
    yield testtemplatefile
    testtemplatefile.unlink()
