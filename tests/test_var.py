import os
import sys

from pew._utils import temp_environ, invoke_pew as invoke

import pytest

def test_set(env1):
    invoke('var','env1','TestVariable','Present')
    check_var = [sys.executable, '-c', "import os; print(os.environ['TestVariable'])"]
    out = invoke('in', 'env1', *check_var).out
    assert 'Present' in out


def test_disp(env1):
    invoke('var','env1','TestVariable','Present')
    out = invoke('var', 'env1', 'TestVariable').out
    assert 'Present' in out


def test_unset(env1):
    invoke('var','env1','TestVariable','Present')
    invoke('var','env1','TestVariable','-u')
    out = invoke('var', 'env1', 'TestVariable').out
    assert 'Present' not in out





