import os

from pew._utils import temp_environ, invoke_pew as invoke


def test_no_pew_in_home(workon_home):
    with temp_environ():
        os.environ['WORKON_HOME'] += '/not_there'
        assert 'does not exist' in invoke('in', 'doesnt_exist').err


def test_invalid_pew_workon_env_name(workon_home):
    with temp_environ():
        assert 'Invalid environment' in invoke('in', '/home/toto').err
