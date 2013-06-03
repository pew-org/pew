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

test_pew_add () {
    full_path=$(echo "pwd" | pew_new "pathtest" | tail -n1)
    echo "pew_add $full_path" | pew_workon "pathtest"
    # Check contents of path file
    path_file=$(echo "pew_sitepackages_dir" | pew_workon "pathtest" | tail -n1)"/_virtualenv_path_extensions.pth"
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

test_pew_add_relative () {
    full_path=$(echo "pwd" | pew_new "pathtest_relative" | tail -n1)
    parent_dir=$(dirname $full_path)
    base_dir=$(basename $full_path)
    echo "pew_add ../$base_dir" | pew_workon "pathtest_relative"
    path_file=$(echo "pew_sitepackages_dir" | pew_workon "pathtest_relative")"/_virtualenv_path_extensions.pth"
    assertTrue "No $parent_dir/$base_dir in \"`cat $path_file`\"" "grep -q \"$parent_dir/$base_dir\" $path_file"
    cd - >/dev/null 2>&1
}

test_pew_add_space () {
	# see #132
	full_path=$(echo "pwd" | pew_new "pathtest_space")
    parent_dir=$(dirname $full_path)
	cd "$WORKON_HOME/pathtest_space"
	mkdir 'a b'
    echo "pew_add 'a b'" | pew_workon "pathtest_space"
    path_file=$(echo "pew_sitepackages_dir" | pew_workon "pathtest_space")"/_virtualenv_path_extensions.pth"
    assertTrue "No 'a b' in \"`cat $path_file`\"" "grep -q 'a b' $path_file"
    cd - >/dev/null 2>&1
}

test_pew_add_ampersand () {
	# see #132
    full_path=$(echo "pwd" | pew_new "pathtest_ampersand")
    parent_dir=$(dirname $full_path)
	cd "$WORKON_HOME/pathtest_ampersand"
	mkdir 'a & b'
	echo "pew_add 'a & b'" | pew_workon "pathtest_ampersand"
    path_file=$(echo "pew_sitepackages_dir" | pew_workon "pathtest_ampersand")"/_virtualenv_path_extensions.pth"
    assertTrue "No 'a & b' in \"`cat $path_file`\"" "grep -q 'a & b' $path_file"
    cd - >/dev/null 2>&1
}

test_pew_add_delete () {
    path_file="./_virtualenv_path_extensions.pth"
    
    # Make sure it was added
    echo "pew_add /full/path" | pew_new "pathtest_delete" >/dev/null 2>&1
	cd $(echo "pew_sitepackages_dir" | pew_workon "pathtest_delete")
    assertTrue "No /full/path in $(cat $path_file)" "grep -q /full/path $path_file"
    # Remove it and verify that change
    echo "pew_add -d /full/path" | pew_workon "pathtest_delete"
    assertFalse "/full/path in `cat $path_file`" "grep -q /full/path $path_file"
    cd - >/dev/null 2>&1
}

test_pew_add_delete_space () {
    path_file="./_virtualenv_path_extensions.pth"
    # Make sure it was added
    echo "pew_add '/full/path with spaces'" | pew_new "pathtest_delete_space" >/dev/null 2>&1
	cd $(echo "pew_sitepackages_dir" | pew_workon "pathtest_delete_space")
    assertTrue "No /full/path with spaces in $(cat $path_file)" "grep -q '/full/path with spaces' $path_file"
    # Remove it and verify that change
    echo "pew_add -d '/full/path with spaces'" | pew_workon "pathtest_delete_space"
    assertFalse "/full/path with spaces in `cat $path_file`" "grep -q '/full/path with spaces' $path_file"
    cd - >/dev/null 2>&1
}

test_pew_add_delete_ampersand () {
    path_file="./_virtualenv_path_extensions.pth"
    # Make sure it was added
    echo "pew_add '/full/path & dir'" | pew_new "pathtest_delete_ampersand" >/dev/null 2>&1
	cd $(echo "pew_sitepackages_dir" | pew_workon "pathtest_delete_ampersand")
    assertTrue "No /full/path & dir in $(cat $path_file)" "grep -q '/full/path & dir' $path_file"
    # Remove it and verify that change
    echo "pew_add -d '/full/path & dir'" | pew_workon "pathtest_delete_ampersand"
    assertFalse "/full/path & dir in `cat $path_file`" "grep -q '/full/path & dir' $path_file"
    cd - >/dev/null 2>&1
}


. "$test_dir/shunit2"
