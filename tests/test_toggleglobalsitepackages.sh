#!/bin/sh

#set -x

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    source "$test_dir/../virtualenvwrapper.sh"
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
    mkvirtualenv --system-site-packages "globaltest"  >/dev/null 2>&1
}

tearDown () {
    deactivate >/dev/null 2>&1
    rmvirtualenv "globaltest" >/dev/null 2>&1
}

test_toggleglobalsitepackages () {
    ngsp_file="`virtualenvwrapper_get_site_packages_dir`/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist" "[ -f \"$ngsp_file\" ]"
    toggleglobalsitepackages -q
    assertFalse "$ngsp_file exists" "[ -f \"$ngsp_file\" ]"
    toggleglobalsitepackages -q
    assertTrue "$ngsp_file does not exist" "[ -f \"$ngsp_file\" ]"
}

test_toggleglobalsitepackages_quiet () {
    assertEquals "Command output is not correct" "Enabled global site-packages" "`toggleglobalsitepackages`"
    assertEquals "Command output is not correct" "Disabled global site-packages" "`toggleglobalsitepackages`"
    
    assertEquals "Command output is not correct" "" "`toggleglobalsitepackages -q`"
    assertEquals "Command output is not correct" "" "`toggleglobalsitepackages -q`"
}

. "$test_dir/shunit2"
