#!/bin/sh

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"


oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

test_pew-mktmpenv_no_name() {
    before=$(pew-ls -b)
    after=$(echo "pew-ls -b" | pew-mktmpenv)
    assertFalse "Environment was not created" "[ \"$before\" = \"$after\" ]"
}

test_pew-mktmpenv_name() {
    echo "" | pew-mktmpenv name-given-by-user >/dev/null 2>&1
    RC=$?
    assertTrue "Error was not detected" "[ $RC -ne 0 ]"
}

test_pew-mktmpenv_virtualenv_args() {
    result=$(echo "test -f $(pew-sitepackages_dir)/../no-global-site-packages.txt && echo ok" | pew-mktmpenv --no-site-packages | tail -n2 | head -n1)""
    assertTrue "tmpenv does not exist" "test $result"
}

test_deactivate() {
    env_name=$(basename $(echo "echo \$VIRTUAL_ENV" | pew-mktmpenv | tail -n2 | head -n1))
    assertTrue "Environment was not created" "test $env_name"
    assertFalse "Environment still exists" "[ -d \"$WORKON_HOME/$env_name\" ]"
}

. "$test_dir/shunit2"
