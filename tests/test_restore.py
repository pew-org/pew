from pew._utils import invoke_pew as invoke

def test_restore(workon_home, env1):
    for site in (workon_home / 'env1' / 'lib').glob('python*/site.py*'):
        site.unlink()
    assert 'ImportError' in invoke('workon', 'env1', inp='python -c ""').err
    r = invoke('restore', 'env1')
    assert 'ImportError' not in invoke('workon', 'env1', inp='python -c ""').err
