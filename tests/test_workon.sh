#!/bin/sh

#set -x

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    echo "" | pew-new "env1" >/dev/null 2>&1
    echo "" | pew-new "env2" >/dev/null 2>&1
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

tearDown () {
    deactivate >/dev/null 2>&1 
}

test_pew-workon () {
    assertSame "env1" $(basename $(echo "echo \$VIRTUAL_ENV" | pew-workon env1 | tail -n1 ))
}

test_no_pew-workon_home () {
    old_home="$WORKON_HOME"
    export WORKON_HOME="$WORKON_HOME/not_there"
    pew-workon should_not_be_created >"$old_home/output" 2>&1
    output=$(cat "$old_home/output")
    assertTrue "Did not see expected message" "echo $output | grep 'does not exist'"
    WORKON_HOME="$old_home"
}

. "$test_dir/shunit2"
