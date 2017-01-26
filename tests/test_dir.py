from pew._utils import invoke_pew as invoke

def test_dir(workon_home, env1):
    assert str(workon_home / 'env1') == invoke('dir', 'env1').out