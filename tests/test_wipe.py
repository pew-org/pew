from pew._utils import invoke_pew as invoke

from utils import xfail_nix, skip_webtest


@xfail_nix
@skip_webtest
def test_wipe(env1):
    assert not invoke('in', 'env1', 'pip', 'install', 'WebTest').err
    assert 'WebTest' in invoke('in', 'env1', 'pip', 'freeze').out
    invoke('wipeenv', 'env1')
    assert 'WebTest' not in invoke('in', 'env1', 'pip', 'freeze').out
