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
    rm -f "$test_dir/requirements.txt"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

test_requirements_file () {
    echo "IPy" > "$test_dir/requirements.txt"
    mkvirtualenv -r "$test_dir/requirements.txt" "env3" >/dev/null 2>&1
    installed=$(pip freeze)
    assertTrue "IPy not found in $installed" "pip freeze | grep IPy"
}

. "$test_dir/shunit2"
