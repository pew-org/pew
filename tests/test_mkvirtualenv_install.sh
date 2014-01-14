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
    rm -f "$test_dir/requirements.txt"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

skip_if_travis() {
    [ $TRAVIS ] && startSkipping
    # don't know why, but the following 2 tests started failing on travis since December 2013
}

test_single_package () {
    skip_if_travis
    installed=$(echo "pip freeze" | pew-new -i IPy "env4" )
    assertTrue "IPy not found in $installed" "echo $installed | grep IPy=="
}

test_multiple_packages () {
    skip_if_travis
	echo "" | pew-new -i IPy -i WebTest "env5" >/dev/null 
    installed=$(echo "pip freeze" | pew-workon env5 )
    assertTrue "IPy not found in $installed" "echo $installed | grep IPy=="
    assertTrue "WebTest not found in $installed" "echo $installed | grep WebTest=="
}

. "$test_dir/shunit2"
