from subprocess import check_call

import pytest

from pew._utils import invoke_pew as invoke


@pytest.yield_fixture()
def to_be_deleted(workon_home):
    envname = 'to_be_deleted'
    invoke('new', envname, '-d')
    yield envname
    assert not (workon_home / envname).exists()


def test_remove(to_be_deleted):
    invoke('rm', to_be_deleted)


def test_no_such_env(workon_home):
    assert not (workon_home / 'not_here').exists()
    check_call('pew rm not_here'.split())
