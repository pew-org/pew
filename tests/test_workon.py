import os
import sys

from pew._utils import temp_environ, invoke_pew as invoke

import pytest

check_env = [sys.executable, '-c', "import os; print(os.environ['VIRTUAL_ENV'])"]

@pytest.mark.skipif(sys.platform == 'win32', reason='cannot supply stdin to powershell')
def test_workon(env1):
    cmd = '{0} {1} "{2}"'.format(*check_env)
    out = invoke('workon', 'env1', inp=cmd).out
    assert 'env1' == os.path.basename(out.splitlines()[-1].strip())


def test_in(env1):
    out = invoke('in', 'env1', *check_env).out
    assert 'env1' == os.path.basename(out.splitlines()[-1].strip())


def test_no_symlink(env1):
    getexe = ['python', '-c', "import sys; print(sys.executable)"]
    env = invoke('in', 'env1', *check_env).out
    exe = invoke('in', 'env1', *getexe).out
    assert exe.lower().startswith(env.lower())


def test_no_pew_workon_home(workon_home):
    with temp_environ():
        os.environ['WORKON_HOME'] += '/not_there'
        assert 'does not exist' in invoke('in', 'doesnt_exist').err

def test_var(envwithvar):
    check_var = [sys.executable, '-c', "import os; print(os.environ['TestVariable'])"]
    out = invoke('in', 'envwithvar', *check_var).out
    assert 'Present' in out


