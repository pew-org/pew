"""Tests for the ``getproject`` subcommand."""

import os

from pew._utils import temp_environ, invoke_pew as invoke
from utils import TemporaryDirectory


def test_getproject(env1):
    """Check that ``getproject`` prints an environment's project directory."""
    with temp_environ():
        os.environ.pop('VIRTUAL_ENV', None)
        with TemporaryDirectory() as tmpdir:
            invoke('setproject', 'env1', tmpdir)
            res = invoke('getproject', 'env1')
            assert not res.err
            assert res.out == tmpdir


def test_project_directory_not_set(env1):
    """Check the error message if no project directory was set.

    If no project directory has been configured for an environment,
    ``getproject`` should quit with an error message.
    """
    name = 'env1'
    with temp_environ():
        os.environ.pop('VIRTUAL_ENV', None)
        with TemporaryDirectory() as tmpdir:
            res = invoke('getproject', name)
            assert not res.out
            assert res.err == (
                "ERROR: no project directory set for Environment '{0}'"
                .format(name)
            )


def test_unknown_environment():
    """Check the error message if passed an unknown environment name.

    If ``getproject`` is invoked with the name of an environment that
    does not exist, the call should fail with an appropriate error
    message.
    """
    name = 'bogus-environment-that-/hopefully/-does-not-exist'
    res = invoke('getproject', name)
    assert not res.out
    assert res.err == "ERROR: Environment '{0}' does not exist.".format(name)


def test_call_without_args_outside_active_venv():
    """Check the error message if called without args outside a virtualenv.

    If ``getproject`` is called without additional arguments outside of
    an active virtualenv, it should print an error message.
    """
    os.environ.pop('VIRTUAL_ENV', None)
    res = invoke('getproject')
    assert not res.out
    assert res.err == "ERROR: no virtualenv active"
