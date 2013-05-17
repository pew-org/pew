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
}

test_get_python_version () {
    expected="$($VIRTUAL_ENV/bin/python -c 'import sys; sys.stdout.write("%s.%s\n" % sys.version_info[:2])')"
    echo "Expecting: $expected"
    vers=$(virtualenvwrapper_get_python_version)
    echo "Got      : $vers"
    assertSame "$expected" "$vers"
}


. "$test_dir/shunit2"
