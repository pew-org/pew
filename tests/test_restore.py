from itertools import chain

from pew._utils import invoke_pew as invoke

def test_restore(workon_home, env1):
    patterns = ['lib*/*/site.py*', 'Lib/site.py*']
    to_be_deleted = set(chain(*((workon_home / 'env1').glob(pat) for pat in patterns)))
    for site in to_be_deleted:
        site.unlink()
    result = invoke('in', 'env1', 'python', '-vc', '')
    assert 'Error' in result.err or 'fail' in result.err
    invoke('restore', 'env1')
    result = invoke('in', 'env1', 'python','-vc', '')
    assert 'Error' not in result.err and 'fail' not in result.err


def test_restore(workon_alt):
    patterns = ['lib*/*/site.py*', 'Lib/site.py*']
    invoke('new','env1','-d','-w',str(workon_alt))
    to_be_deleted = set(chain(*((workon_alt / 'env1').glob(pat) for pat in patterns)))
    for site in to_be_deleted:
        site.unlink()
    result = invoke('in', '-w', str(workon_alt), 'env1', 'python', '-vc', '')
    assert 'Error' in result.err or 'fail' in result.err
    invoke('restore', 'env1', '-w', str(workon_alt))
    result = invoke('in', '-w', str(workon_alt), 'env1', 'python','-vc', '')
    assert 'Error' not in result.err and 'fail' not in result.err
    invoke('rm','-w', str(workon_alt), 'env1')