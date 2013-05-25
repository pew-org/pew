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

# oneTimeTearDown() {
#     rm -rf "$WORKON_HOME"
#     rm -rf "$PROJECT_HOME"
# }

setUp () {
    echo
    rm -f "$TMPDIR/catch_output"
	VIRTUAL_ENV=""
}

test_activate () {
    echo "" | mkproject myproject >/dev/null 2>&1
    cd $TMPDIR
    assertSame "" "$VIRTUAL_ENV"
    venv=$(echo "echo \$VIRTUAL_ENV" | workon myproject | tail -n1)
    assertSame "myproject" "$(basename $venv)"
}

test_space_in_path () {
    old_project_home="$PROJECT_HOME"
    PROJECT_HOME="$PROJECT_HOME/with spaces"
    mkdir -p "$PROJECT_HOME"
    echo "" | mkproject "myproject" >/dev/null 2>&1
    cd $TMPDIR
    venv=$(echo "echo \$VIRTUAL_ENV" | workon myproject | tail -n1)
    assertSame "myproject" "$(basename $venv)"
    PROJECT_HOME="$old_project_home"
}


. "$test_dir/shunit2"
