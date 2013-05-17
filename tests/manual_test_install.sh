#!/bin/sh
#
# Test installation of virtualenvwrapper in a new virtualenv.
#

test_dir=$(dirname $0)
source "$test_dir/../virtualenvwrapper.sh"

export WORKON_HOME="${TMPDIR:-/tmp}/WORKON_HOME"

VERSION=$(python setup.py --version)

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
}

setUp () {
    echo
}

test_build_ok () {
    (cd "$test_dir/.." && make sdist)
    outcome=$?
 	assertSame "0" "$outcome"
}

test_install () {
    dist_dir=$(dirname $test_dir)/dist
    pip install "$dist_dir/virtualenvwrapper-$VERSION.tar.gz"
    RC=$?
    assertTrue "Error code $RC" "[ $RC -eq 0 ]"
    assertTrue "Missing wrapper script" "[ -f $WORKON_HOME/installtest/bin/virtualenvwrapper.sh ]"
}

. "$test_dir/shunit2"
