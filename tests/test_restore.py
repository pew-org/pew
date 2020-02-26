from itertools import chain

from pew._utils import invoke_pew as invoke


def test_restore(workon_home, env1):
    patterns = ['lib*/*/site.py*', 'Lib/site.py*']
    to_be_deleted = set(chain(*((workon_home / 'env1').glob(pat) for pat in patterns)))
    for site in to_be_deleted:
        try:
            site.unlink()
        except FileNotFoundError:
            pass # multiple links to the same file might appear in to_be_deleted
    result = invoke('in', 'env1', 'python', '-vc', '')
    assert 'Error' in result.err or 'fail' in result.err
    invoke('restore', 'env1')
    result = invoke('in', 'env1', 'python', '-vc', '')
    assert 'Error' not in result.err and 'fail' not in result.err
