import os
import sys
from subprocess import check_call, CalledProcessError
from pathlib import Path
from shutil import rmtree
from tempfile import gettempdir

import pytest

from pew._utils import temp_environ, invoke_pew as invoke
from utils import skip_windows


@pytest.yield_fixture(scope='session')
def project_home():
    tmpdir = os.environ.get('TMPDIR', gettempdir())
    project = Path(tmpdir) / 'PROJECT_HOME'
    os.environ['PROJECT_HOME'] = str(project)

    rmtree(str(project), ignore_errors=True)
    project.mkdir(parents=True)
    yield project
    rmtree(str(project))


@pytest.yield_fixture()
def project(workon_home, project_home):
    projname = 'project1'
    invoke('mkproject', projname, '-d')
    yield projname
    invoke('rm', projname)
    rmtree(str(project_home / projname))


def test_create_directories(workon_home, project_home, project):
    assert (workon_home / project).exists()
    assert (project_home / project).exists()

check_env = [sys.executable, '-c', "import os; print(os.environ['VIRTUAL_ENV'])"]


def test_create_virtualenv(project_home, project):
    env = Path(invoke('in', project, *check_env).out)
    assert project == env.name
    with (env / '.project').open() as f:
        assert str(project_home.absolute() / project) == f.read().strip()


def test_no_project_home(project_home):
    with temp_environ():
        os.environ['PROJECT_HOME'] += '/not_there'
        with pytest.raises(CalledProcessError):
            check_call('pew mkproject whatever -d'.split())


def test_project_exists(project):
    with pytest.raises(CalledProcessError):
        check_call('pew mkproject {0} -d'.format(project).split())


def test_same_workon_and_project_home(workon_home, project_home):
    with temp_environ():
        os.environ['PROJECT_HOME'] = str(workon_home)
        envname = 'whatever'
        with pytest.raises(CalledProcessError):
            check_call('pew mkproject {0} -d'.format(envname).split())
        assert (workon_home / envname).exists()
        assert not (project_home / envname).exists()


def test_list_templates(testtemplate):
    assert 'test' in invoke('mkproject', '-l').out


@skip_windows(reason='cannot scripts written in an arbitrary language on '
                     'windows by relying on the shebang')
def test_apply_template(project_home, testtemplate):
    projname = 'project1'
    invoke('mkproject', '-t', 'test', projname, '-d')
    testfile = project_home / projname / 'TEST_FILE'
    assert testfile.exists()
    with testfile.open() as f:
        assert projname in f.read()
    invoke('rm', projname)
    rmtree(str(project_home / projname))
