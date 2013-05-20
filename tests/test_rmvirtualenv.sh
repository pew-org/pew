#!/bin/sh

#set -x

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

test_remove () {
    echo "" | mkvirtualenv "deleteme" >/dev/null 2>&1
    assertTrue "[ -d $WORKON_HOME/deleteme ]"
    rmvirtualenv "deleteme"
    assertFalse "[ -d $WORKON_HOME/deleteme ]"
}

test_within_virtualenv () {
    echo "" | mkvirtualenv "deleteme" >/dev/null 2>&1
    assertTrue "[ -d $WORKON_HOME/deleteme ]"
    #cdvirtualenv
    #assertSame "$VIRTUAL_ENV" "$(pwd)"
    rmvirtualenv "deleteme"
    #assertSame "$WORKON_HOME" "$(pwd)"
    assertFalse "[ -d $WORKON_HOME/deleteme ]"
}

test_rm_aliased () {
    echo "" | mkvirtualenv "deleteme" >/dev/null 2>&1
    alias rm='rm -i'
    rmvirtualenv "deleteme"
    unalias rm
}

test_no_such_env () {
    assertFalse "[ -d $WORKON_HOME/deleteme ]"
    assertTrue "rmvirtualenv deleteme"
}

test_no_workon_home () {
    old_home="$WORKON_HOME"
    export WORKON_HOME="$WORKON_HOME/not_there"
    rmvirtualenv should_not_be_created >"$old_home/output" 2>&1
    output=$(cat "$old_home/output")
    assertTrue "Did not see expected message" "echo $output | grep 'No such file'"
    WORKON_HOME="$old_home"
}


. "$test_dir/shunit2"
