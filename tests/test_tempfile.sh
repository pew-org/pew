#!/bin/sh

#set -x

test_dir=$(cd $(dirname $0) && pwd)

tmplocation=${TMPDIR:-/tmp}
export WORKON_HOME="$(echo ${tmplocation}/WORKON_HOME | sed 's|//|/|g')"

export HOOK_VERBOSE_OPTION=-v

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    source "$test_dir/../virtualenvwrapper.sh"
    echo $PYTHONPATH
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

test_tempfile () {
    filename=$(virtualenvwrapper_tempfile hook)
    assertTrue "Filename is empty" "[ ! -z \"$filename\" ]"
    rm -f $filename
    comparable_tmpdir=$(echo $tmplocation | sed 's|/$||')
    comparable_dirname=$(dirname $filename | sed 's|/$||')
    assertSame "Temporary directory \"$tmplocation\" and path not the same for $filename" "$comparable_tmpdir" "$comparable_dirname"
    assertTrue "virtualenvwrapper-hook not in filename." "echo $filename | grep virtualenvwrapper-hook"
}

test_no_such_tmpdir () {
    old_tmpdir="$TMPDIR"
    export TMPDIR="$tmplocation/does-not-exist"
    virtualenvwrapper_run_hook "initialize" >/dev/null 2>&1
    RC=$?
    assertSame "Unexpected exit code $RC" "1" "$RC"
    TMPDIR="$old_tmpdir"
}

test_tmpdir_not_writable () {
    old_tmpdir="$TMPDIR"
    export TMPDIR="$tmplocation/cannot-write"
    mkdir "$TMPDIR"
    chmod ugo-w "$TMPDIR"
    virtualenvwrapper_run_hook "initialize" >/dev/null 2>&1
    RC=$?
    assertSame "Unexpected exit code $RC" "1" "$RC"
    chmod ugo+w "$TMPDIR"
    rmdir "$TMPDIR"
    TMPDIR="$old_tmpdir"
}

. "$test_dir/shunit2"
