from pew._utils import invoke_pew as invoke

from utils import connection_required


@connection_required
def test_wipe(env1):
    assert invoke('in', 'env1', 'pip', 'install', 'WebTest').returncode == 0
    assert 'WebTest' in invoke('in', 'env1', 'pip', 'freeze').out
    invoke('wipeenv', 'env1')
    assert 'WebTest' not in invoke('in', 'env1', 'pip', 'freeze').out
