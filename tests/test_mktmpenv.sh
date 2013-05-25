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

test_mktmpenv_no_name() {
    before=$(lsvirtualenv -b)
    after=$(echo "lsvirtualenv -b" | mktmpenv)
    assertFalse "Environment was not created" "[ \"$before\" = \"$after\" ]"
}

test_mktmpenv_name() {
    echo "" | mktmpenv name-given-by-user >/dev/null 2>&1
    RC=$?
    assertTrue "Error was not detected" "[ $RC -ne 0 ]"
}

test_mktmpenv_virtualenv_args() {
    result=$(echo "test -f $(sitepackages_dir)/../no-global-site-packages.txt && echo ok" | mktmpenv --no-site-packages | tail -n2 | head -n1)""
    assertTrue "tmpenv does not exist" "test $result"
}

test_deactivate() {
    env_name=$(basename $(echo "echo \$VIRTUAL_ENV" | mktmpenv | tail -n2 | head -n1))
    assertTrue "Environment was not created" "test $env_name"
    assertFalse "Environment still exists" "[ -d \"$WORKON_HOME/$env_name\" ]"
}

. "$test_dir/shunit2"
