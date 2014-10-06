from pew._utils import invoke_pew as invoke

def test_restore(workon_home, env1):
    for site in (workon_home / 'env1').glob('lib*/*/site.py*'):
        site.unlink()
    result = invoke('workon', 'env1', inp='python -vc ""')
    assert 'Error' in result.err or 'fail' in result.err
    r = invoke('restore', 'env1')
    result = invoke('workon', 'env1', inp='python -vc ""')
    assert 'Error' not in result.err and 'fail' not in result.err
