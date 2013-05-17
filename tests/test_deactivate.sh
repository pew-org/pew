#!/bin/sh

#set -x

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    source "$test_dir/../virtualenvwrapper.sh"
    mkvirtualenv "env1"
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

test_deactivate () {
    workon env1
    assertNotNull "$VIRTUAL_ENV"
    deactivate
    assertNull "$VIRTUAL_ENV"
    assertFalse virtualenvwrapper_verify_active_environment    
}

test_deactivate_hooks () {
    workon env1

    for t in pre post
    do
        echo "echo GLOBAL ${t}deactivate \$VIRTUALENVWRAPPER_LAST_VIRTUAL_ENV >> $test_dir/catch_output" > "$WORKON_HOME/${t}deactivate"
        echo "echo ENV ${t}deactivate \$VIRTUALENVWRAPPER_LAST_VIRTUAL_ENV >> $test_dir/catch_output" > "$WORKON_HOME/env1/bin/${t}deactivate"
    done

    touch "$test_dir/catch_output"

    deactivate

    output=$(cat "$test_dir/catch_output")
    expected="ENV predeactivate
GLOBAL predeactivate
ENV postdeactivate $WORKON_HOME/env1
GLOBAL postdeactivate $WORKON_HOME/env1"
    assertSame "$expected" "$output"
    
    for t in pre post
    do
        rm -f "$WORKON_HOME/env1/bin/${t}activate"
        rm -f "$WORKON_HOME/${t}activate"
    done
}

. "$test_dir/shunit2"
