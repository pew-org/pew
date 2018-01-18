from pew._utils import invoke_pew as invoke

from utils import connection_required


@connection_required
def test_wipe(env1):
    proc = invoke('in', 'env1', 'pip', 'install', 'WebTest')
    assert proc.returncode == 0, proc.err

    proc = invoke('in', 'env1', 'pip', 'freeze')
    assert proc.returncode == 0 and 'WebTest' in proc.out

    proc = invoke('wipeenv', 'env1')
    assert proc.returncode == 0, proc.err

    proc = invoke('in', 'env1', 'pip', 'freeze')
    assert proc.returncode == 0 and 'WebTest' not in proc.out
