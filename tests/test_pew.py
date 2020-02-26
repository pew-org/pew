import os

import pew

import pytest

@pytest.mark.skipif(os.environ.get('NIX'), reason='Needed only outside of Nix')
def test_current_pew():
    "Sometimes the tox test runner won't pick up the correct/current project"
    assert not pew.__file__.startswith('/nix')
