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
}

test_get_site_packages_dir () {
    d=$(echo "sitepackages_dir" | mkvirtualenv "lssitepackagestest" | tail -n1 )
    echo "site-packages in $d"
    assertTrue "site-packages dir $d does not exist" "[ -d $d ]"
}

test_lssitepackages () {
    contents=$(echo "lssitepackages" | mkvirtualenv "lssitepackagestest" | tail -n1)
    actual=$(echo $contents | grep easy-install.pth)
    expected=$(echo $contents)
    assertSame "$expected" "$actual"
}

test_lssitepackages_add2virtualenv () {
    full_path=$(echo "pwd" | mkvirtualenv "lssitepackagestest" | tail -n1)
    parent_dir=$(dirname $full_path)
    base_dir=$(basename $full_path)
    contents=$(echo "add2virtualenv '../$base_dir'; lssitepackages" | workon "lssitepackagestest" | tail -n1)
    actual=$(echo $contents | grep $base_dir)
    expected=$(echo $contents)
    assertSame "$expected" "$actual"
}


. "$test_dir/shunit2"
