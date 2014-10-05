import os
import sys

from pew._utils import temp_environ, invoke_pew as invoke

check_env = sys.executable + ''' -c "import os; print(os.environ['VIRTUAL_ENV'])"'''


def test_workon(env1):
    out = invoke('workon', 'env1', inp=check_env).out
    assert 'env1' == os.path.basename(out.splitlines()[-1].strip())


def test_no_symlink(env1):
    getexe = 'python -c "import sys; print(sys.executable)"'
    env = invoke('workon', 'env1', inp=check_env).out
    exe = invoke('workon', 'env1', inp=getexe).out
    assert exe.startswith(env)


def test_no_pew_workon_home(workon_home):
    with temp_environ():
        os.environ['WORKON_HOME'] += '/not_there'
        assert 'does not exist' in invoke('workon', 'doesnt_exist').err
