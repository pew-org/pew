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
def env1(workon_home):
    invoke('new', 'env1', '-d')
    yield
    invoke('rm', 'env1')


@pytest.yield_fixture()
def env2(workon_home):
    invoke('new', 'env2', '-d')
    yield
    invoke('rm', 'env2')

@pytest.yield_fixture()
def testpackageenv(workon_home):
    testpackage = str(Path(__file__).parent / 'testpackage')
    invoke('new', 'source', '-d')
    invoke('in', 'source', 'python', 'setup.py', 'install', cwd=testpackage)
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


