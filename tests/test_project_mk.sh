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
    source "$test_dir/../virtualenvwrapper.sh"
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
    mkproject myproject1 >/dev/null 2>&1
    assertTrue "env directory not created" "[ -d $WORKON_HOME/myproject1 ]"
    assertTrue "project directory not created" "[ -d $PROJECT_HOME/myproject1 ]"
}

test_create_virtualenv () {
    mkproject myproject2 >/dev/null 2>&1
    assertSame "myproject2" $(basename "$VIRTUAL_ENV")
    assertSame "$PROJECT_HOME/myproject2" "$(cat $VIRTUAL_ENV/.project)"
}

test_hooks () {
    echo "echo GLOBAL premkproject \`pwd\` \"\$@\" >> \"$WORKON_HOME/catch_output\"" >> "$VIRTUALENVWRAPPER_HOOK_DIR/premkproject"
    chmod +x "$VIRTUALENVWRAPPER_HOOK_DIR/premkproject"
    echo "echo GLOBAL postmkproject \`pwd\` >> $WORKON_HOME/catch_output" > "$VIRTUALENVWRAPPER_HOOK_DIR/postmkproject"

    mkproject myproject3 >/dev/null 2>&1

    output=$(cat "$WORKON_HOME/catch_output")

    expected="GLOBAL premkproject $PROJECT_HOME myproject3
GLOBAL postmkproject $PROJECT_HOME/myproject3"
    assertSame "$expected" "$output"

    rm -f "$VIRTUALENVWRAPPER_HOOK_DIR/premkproject"
    rm -f "$VIRTUALENVWRAPPER_HOOK_DIR/postmkproject"
}

test_no_project_home () {
    old_home="$PROJECT_HOME"
    export PROJECT_HOME="$PROJECT_HOME/not_there"
    output=`mkproject should_not_be_created 2>&1`
    assertTrue "Did not see expected message" "echo $output | grep 'does not exist'"
    PROJECT_HOME="$old_home"
}

test_project_exists () {
    mkproject myproject4 >/dev/null 2>&1
    output=`mkproject myproject4 2>&1`
    assertTrue "Did not see expected message 'already exists' in: $output" "echo $output | grep 'already exists'"
}

test_same_workon_and_project_home () {
    old_project_home="$PROJECT_HOME"
    export PROJECT_HOME="$WORKON_HOME"
    mkproject myproject5 >/dev/null 2>&1
    assertTrue "env directory not created" "[ -d $WORKON_HOME/myproject1 ]"
    assertTrue "project directory was created" "[ -d $old_project_home/myproject1 ]"
    PROJECT_HOME="$old_project_home"
}

test_alternate_linkage_filename () {
    export VIRTUALENVWRAPPER_PROJECT_FILENAME=".not-project"
    mkproject myproject6 >/dev/null 2>&1
    assertSame "myproject6" $(basename "$VIRTUAL_ENV")
    assertSame "$PROJECT_HOME/myproject6" "$(cat $VIRTUAL_ENV/.not-project)"
    export VIRTUALENVWRAPPER_PROJECT_FILENAME=".project"
}

. "$test_dir/shunit2"
