#!/bin/sh

#set -x

test_dir=$(dirname $0)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"
export PROJECT_HOME="$(echo ${TMPDIR:-/tmp}/PROJECT_HOME | sed 's|//|/|g')"

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    rm -rf "$PROJECT_HOME"
    mkdir -p "$PROJECT_HOME"
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
    rm -rf "$PROJECT_HOME"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
    unset VIRTUALENVWRAPPER_INITIALIZED
}

test_initialize() {
    source "$test_dir/../virtualenvwrapper.sh"
    for hook in  premkproject postmkproject prermproject postrmproject
    do
        assertTrue "Global $hook was not created" "[ -f $WORKON_HOME/$hook ]"
        assertTrue "Global $hook is not executable" "[ -x $WORKON_HOME/$hook ]"
    done
}

test_initialize_hook_dir() {
    export VIRTUALENVWRAPPER_HOOK_DIR="$WORKON_HOME/hooks"
    mkdir -p "$VIRTUALENVWRAPPER_HOOK_DIR"
    source "$test_dir/../virtualenvwrapper.sh"
    for hook in  premkproject postmkproject prermproject postrmproject
    do
        assertTrue "Global $hook was not created" "[ -f $VIRTUALENVWRAPPER_HOOK_DIR/$hook ]"
        assertTrue "Global $hook is not executable" "[ -x $VIRTUALENVWRAPPER_HOOK_DIR/$hook ]"
    done
    VIRTUALENVWRAPPER_HOOK_DIR="$WORKON_HOME"
}

test_virtualenvwrapper_verify_project_home() {
    assertTrue "PROJECT_HOME not verified" virtualenvwrapper_verify_project_home
}

test_virtualenvwrapper_verify_project_home_missing_dir() {
    old_home="$PROJECT_HOME"
    PROJECT_HOME="$PROJECT_HOME/not_there"
    assertFalse "PROJECT_HOME verified unexpectedly" virtualenvwrapper_verify_project_home
    PROJECT_HOME="$old_home"
}

. "$test_dir/shunit2"
