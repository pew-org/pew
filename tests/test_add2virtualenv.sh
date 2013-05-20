#!/bin/sh
# SKIP

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

test_add2virtualenv () {
    full_path=$(echo "pwd" | mkvirtualenv "pathtest" | tail -n1)
    echo "add2virtualenv $full_path" | workon "pathtest"
    # Check contents of path file
    path_file=$(echo "sitepackages_dir" | workon "pathtest")"/_virtualenv_path_extensions.pth"
    assertTrue "No $full_path in $(cat $path_file)" "grep -q $full_path $path_file"
    assertTrue "No path insert code in $(cat $path_file)" "grep -q sys.__egginsert $path_file"
    # Check the path we inserted is actually at the top
    expected="$full_path"
    actual=$($WORKON_HOME/pathtest/bin/python -c "import sys; sys.stdout.write(sys.path[1]+'\n')")
    assertSame "$expected" "$actual"
    # Make sure the temporary file created
    # during the edit was removed
    assertFalse "Temporary file ${path_file}.tmp still exists" "[ -f ${path_file}.tmp ]"
    cd - >/dev/null 2>&1
}

test_add2virtualenv_relative () {
    full_path=$(echo "pwd" | mkvirtualenv "pathtest_relative")
    parent_dir=$(dirname $full_path)
    base_dir=$(basename $full_path)
    echo "add2virtualenv ../$base_dir" | workon "pathtest_relative"
    path_file=$(echo "sitepackages_dir" | workon "pathtest_relative")"/_virtualenv_path_extensions.pth"
    assertTrue "No $parent_dir/$base_dir in \"`cat $path_file`\"" "grep -q \"$parent_dir/$base_dir\" $path_file"
    cd - >/dev/null 2>&1
}

test_add2virtualenv_space () {
	# see #132
	full_path=$(echo "pwd" | mkvirtualenv "pathtest_space")
    parent_dir=$(dirname $full_path)
	cd "$WORKON_HOME/pathtest_space"
	mkdir 'a b'
    echo "add2virtualenv 'a b'" | workon "pathtest_space"
    path_file=$(echo "sitepackages_dir" | workon "pathtest_space")"/_virtualenv_path_extensions.pth"
    assertTrue "No 'a b' in \"`cat $path_file`\"" "grep -q 'a b' $path_file"
    cd - >/dev/null 2>&1
}

test_add2virtualenv_ampersand () {
	# see #132
    full_path=$(echo "pwd" | mkvirtualenv "pathtest_ampersand")
    parent_dir=$(dirname $full_path)
	cd "$WORKON_HOME/pathtest_ampersand"
	mkdir 'a & b'
	echo "add2virtualenv 'a & b'" | workon "pathtest_ampersand"
    path_file=$(echo "sitepackages_dir" | workon "pathtest_ampersand")"/_virtualenv_path_extensions.pth"
    assertTrue "No 'a & b' in \"`cat $path_file`\"" "grep -q 'a & b' $path_file"
    cd - >/dev/null 2>&1
}

test_add2virtualenv_delete () {
    path_file="./_virtualenv_path_extensions.pth"
    
    #cd sitepackages_dir
    # Make sure it was added
    echo "add2virtualenv /full/path" | mkvirtualenv "pathtest_delete" >/dev/null 2>&1
    assertTrue "No /full/path in $(cat $path_file)" "grep -q /full/path $path_file"
    # Remove it and verify that change
    echo "add2virtualenv -d /full/path" | workon "pathtest_delete"
    assertFalse "/full/path in `cat $path_file`" "grep -q /full/path $path_file"
    cd - >/dev/null 2>&1
}

test_add2virtualenv_delete_space () {
    path_file="./_virtualenv_path_extensions.pth"
    # cd sitepackages_dir   
    # Make sure it was added
    echo "add2virtualenv '/full/path with spaces'" | mkvirtualenv "pathtest_delete_space" >/dev/null 2>&1
    assertTrue "No /full/path with spaces in $(cat $path_file)" "grep -q '/full/path with spaces' $path_file"
    # Remove it and verify that change
    echo "add2virtualenv -d '/full/path with spaces'" | workon "pathtest_delete_space"
    assertFalse "/full/path with spaces in `cat $path_file`" "grep -q '/full/path with spaces' $path_file"
    cd - >/dev/null 2>&1
}

test_add2virtualenv_delete_ampersand () {
    path_file="./_virtualenv_path_extensions.pth"
    # cd sitepackages_dir
    # Make sure it was added
    echo "add2virtualenv '/full/path & dir'" | mkvirtualenv "pathtest_delete_ampersand" >/dev/null 2>&1
    assertTrue "No /full/path & dir in $(cat $path_file)" "grep -q '/full/path & dir' $path_file"
    # Remove it and verify that change
    echo "add2virtualenv -d '/full/path & dir'" | workon "pathtest_delete_ampersand"
    assertFalse "/full/path & dir in `cat $path_file`" "grep -q '/full/path & dir' $path_file"
    cd - >/dev/null 2>&1
}


. "$test_dir/shunit2"
