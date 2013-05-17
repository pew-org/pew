#!/bin/sh

#set -x

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    unset VIRTUAL_ENV
    source "$test_dir/../virtualenvwrapper.sh"
    mkvirtualenv cd-test
    deactivate
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
    workon cd-test
}

tearDown () {
    deactivate >/dev/null 2>&1
}

test_cdvirtual() {
    start_dir="$(pwd)"
    cdvirtualenv
    assertSame "$VIRTUAL_ENV" "$(pwd)"
    cdvirtualenv bin
    assertSame "$VIRTUAL_ENV/bin" "$(pwd)"
    cd "$start_dir"
}

test_cdsitepackages () {
    start_dir="$(pwd)"
    cdsitepackages
    pyvers=$(python -V 2>&1 | cut -f2 -d' ' | cut -f1-2 -d.)
    sitepackages="$VIRTUAL_ENV/lib/python${pyvers}/site-packages"
    assertSame "$sitepackages" "$(pwd)"
    cd "$start_dir"
}

test_cdsitepackages_with_arg () {
    start_dir="$(pwd)"
    pyvers=$(python -V 2>&1 | cut -f2 -d' ' | cut -f1-2 -d.)
    sitepackage_subdir="$VIRTUAL_ENV/lib/python${pyvers}/site-packages/subdir"
    mkdir -p "${sitepackage_subdir}"
    cdsitepackages subdir
    assertSame "$sitepackage_subdir" "$(pwd)"
    cd "$start_dir"
}

test_cdvirtualenv_no_workon_home () {
    old_home="$WORKON_HOME"
    export WORKON_HOME="$WORKON_HOME/not_there"
    cdvirtualenv >"$old_home/output" 2>&1
    output=$(cat "$old_home/output")
    assertTrue "Did not see expected message" "echo $output | grep 'does not exist'"
    WORKON_HOME="$old_home"
}

test_cdsitepackages_no_workon_home () {
    deactivate 2>&1
    old_home="$WORKON_HOME"
    cd "$WORKON_HOME"
    export WORKON_HOME="$WORKON_HOME/not_there"
    assertFalse "Was able to change to site-packages" cdsitepackages
    assertSame "$old_home" "$(pwd)"
    WORKON_HOME="$old_home"
}


. "$test_dir/shunit2"
