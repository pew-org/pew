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


test_virtualenvwrapper_space_in_workon_home() {
    before="$WORKON_HOME"
    export WORKON_HOME="$WORKON_HOME/this has spaces"
 	expected="$WORKON_HOME"
    mkdir -p "$expected"
    pew-ls
    RC=$?
    assertSame "$expected" "$WORKON_HOME"
    assertSame "0" "$RC"
    export WORKON_HOME="$before"
}

. "$test_dir/shunit2"
