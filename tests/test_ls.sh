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
    d=$(echo "pew-sitepackages_dir" | pew-new "pew-lssitepackagestest" | tail -n1 )
    echo "site-packages in $d"
    assertTrue "site-packages dir $d does not exist" "[ -d $d ]"
}

test_pew-lssitepackages () {
    contents=$(echo "pew-lssitepackages" | pew-new "pew-lssitepackagestest" | tail -n1)
    actual=$(echo $contents | grep easy-install.pth)
    expected=$(echo $contents)
    assertSame "$expected" "$actual"
}

test_pew-lssitepackages_pew-add () {
    full_path=$(echo "pwd" | pew-new "pew-lssitepackagestest" | tail -n1)
    parent_dir=$(dirname $full_path)
    base_dir=$(basename $full_path)
    contents=$(echo "pew-add '../$base_dir'; pew-lssitepackages" | pew-workon "pew-lssitepackagestest" | tail -n1)
    actual=$(echo $contents | grep $base_dir)
    expected=$(echo $contents)
    assertSame "$expected" "$actual"
}


. "$test_dir/shunit2"
