#!/bin/sh

#set -x

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
    echo "" | pew_new "globaltest"  >/dev/null 2>&1
}

tearDown () {
    pew_rm "globaltest" >/dev/null 2>&1
}

test_pew_toggleglobalsitepackages () {
    ngsp_file=$(echo pew_sitepackages_dir | pew_workon globaltest | tail -n1)"/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist" "[ -f \"$ngsp_file\" ]"
    echo "pew_toggleglobalsitepackages -q" | pew_workon globaltest
    assertFalse "$ngsp_file exists" "[ -f \"$ngsp_file\" ]"
    echo "pew_toggleglobalsitepackages -q" | pew_workon globaltest
    assertTrue "$ngsp_file does not exist" "[ -f \"$ngsp_file\" ]"
}

test_pew_toggleglobalsitepackages_quiet () {
    assertEquals "Command output is not correct" "Enabled global site-packages" "$(echo pew_toggleglobalsitepackages | pew_workon globaltest | tail -n1)"
    assertEquals "Command output is not correct" "Disabled global site-packages" "$(echo pew_toggleglobalsitepackages | pew_workon globaltest | tail -n1)"
    
    assertEquals "Command output is not correct" "" "$(echo pew_toggleglobalsitepackages -q | pew_workon globaltest | tail -n1)"
    assertEquals "Command output is not correct" "" "$(echo pew_toggleglobalsitepackages -q | pew_workon globaltest | tail -n1)"
}

. "$test_dir/shunit2"
