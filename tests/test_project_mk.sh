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
    rm -f "$WORKON_HOME/catch_output"
}

tearDown () {
    type deactivate >/dev/null 2>&1 && deactivate
}

test_create_directories () {
    echo "" | pew-mkproject myproject1 >/dev/null 2>&1
    assertTrue "env directory not created" "[ -d $WORKON_HOME/myproject1 ]"
    assertTrue "project directory not created" "[ -d $PROJECT_HOME/myproject1 ]"
}

test_create_virtualenv () {
    echo "" | pew-mkproject myproject2 >/dev/null 2>&1
	venv=$(echo "echo \$VIRTUAL_ENV" | pew-workon myproject2 | tail -n1)
    assertSame "myproject2" $(basename "$venv")
    assertSame "$PROJECT_HOME/myproject2" "$(cat $venv/.project)"
}

test_no_project_home () {
    old_home="$PROJECT_HOME"
    export PROJECT_HOME="$PROJECT_HOME/not_there"
    output=`pew-mkproject should_not_be_created 2>&1`
    assertTrue "Did not see expected message" "echo $output | grep 'does not exist'"
    PROJECT_HOME="$old_home"
}

test_project_exists () {
    echo "" | pew-mkproject myproject4 >/dev/null 2>&1
    output=`pew-mkproject myproject4 2>&1`
    assertTrue "Did not see expected message 'already exists' in: $output" "echo $output | grep 'already exists'"
}

test_same_pew-workon_and_project_home () {
    old_project_home="$PROJECT_HOME"
    export PROJECT_HOME="$WORKON_HOME"
    echo "" | pew-mkproject myproject5 >/dev/null 2>&1
    assertTrue "env directory not created" "[ -d $WORKON_HOME/myproject1 ]"
    assertTrue "project directory was created" "[ -d $old_project_home/myproject1 ]"
    PROJECT_HOME="$old_project_home"
}

. "$test_dir/shunit2"
