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

# oneTimeTearDown() {
#     rm -rf "$WORKON_HOME"
#     rm -rf "$PROJECT_HOME"
# }

setUp () {
    echo
    rm -f "$TMPDIR/catch_output"
}

test_activate () {
    mkproject myproject >/dev/null 2>&1
    deactivate
    cd $TMPDIR
    assertSame "" "$VIRTUAL_ENV"
    workon myproject
    assertSame "myproject" "$(basename $VIRTUAL_ENV)"
    assertSame "$PROJECT_HOME/myproject" "$(pwd)"
    deactivate
}

test_space_in_path () {
    old_project_home="$PROJECT_HOME"
    PROJECT_HOME="$PROJECT_HOME/with spaces"
    mkdir -p "$PROJECT_HOME"
    mkproject "myproject" >/dev/null 2>&1
    deactivate
    cd $TMPDIR
    workon "myproject"
    assertSame "myproject" "$(basename $VIRTUAL_ENV)"
    assertSame "$PROJECT_HOME/myproject" "$(pwd)"
    deactivate
    PROJECT_HOME="$old_project_home"
}


. "$test_dir/shunit2"
