import pew


def test_current_pew():
    "Sometimes the tox test runner won't pick up the correct/current project"
    assert not pew.__file__.startswith('/nix')
