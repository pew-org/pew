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
	ln -s $(readlink -f $test_dir/testtemplate/template.py) $WORKON_HOME/template_test
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
    rm -rf "$PROJECT_HOME"
}

setUp () {
    echo
    rm -f "$TMPDIR/catch_output"
}

test_list_templates () {
    output=$(echo "" | pew_mkproject -l 2>&1)
    assertTrue "Did not find test template in \"$output\"" "echo \"$output\" | grep -q 'test'"
}

test_apply_template () {
    echo "" | pew_mkproject -t test proj1
    assertTrue "Test file not created" "[ -f $PROJECT_HOME/proj1/TEST_FILE ]"
    assertTrue "project name not found" "grep -q proj1 $PROJECT_HOME/proj1/TEST_FILE"
}

. "$test_dir/shunit2"
