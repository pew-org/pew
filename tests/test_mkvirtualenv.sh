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

test_create() {
    echo "" | mkvirtualenv "env1" >/dev/null 2>&1
    assertTrue "Environment directory was not created" "[ -d $WORKON_HOME/env1 ]"
}

test_activates () {
    #assertTrue virtualenvwrapper_verify_active_environment
    assertSame "env2" $(basename $(echo "echo \$VIRTUAL_ENV" | mkvirtualenv "env2" | tail -n1))
}


test_no_virtualenv () {
    old_path="$PATH"
    PATH="/bin:/usr/sbin:/sbin"
    assertFalse "Found virtualenv in $(which virtualenv)" "which virtualenv"
    mkvirtualenv should_not_be_created 2>/dev/null
    RC=$?
    # Restore the path before testing because
    # the test script depends on commands in the
    # path.
    export PATH="$old_path"
    assertSame "127" "$RC"
}

test_no_args () {
    mkvirtualenv 2>/dev/null 1>&2
    RC=$?
    assertSame "2" "$RC"
}


test_mkvirtualenv_sitepackages () {
    # This part of the test is not reliable because
    # creating a new virtualenv from inside the
    # tox virtualenv inherits the setting from there.
    # Without the option, verify that site-packages are copied.
	echo "" | mkvirtualenv "with_sp" --system-site-packages >/dev/null 2>&1
    ngsp_file=$(echo "sitepackages_dir" | workon with_sp | tail -n1 )"/../no-global-site-packages.txt"
    assertFalse "$ngsp_file exists" "[ -f \"$ngsp_file\" ]"
    
    # With the argument, verify that they are not copied.
    echo "" | mkvirtualenv "without_sp" --no-site-packages >/dev/null
    ngsp_file=$(echo "sitepackages_dir" | workon without_sp | tail -n1 )"/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist" "[ -f \"$ngsp_file\" ]"
}


. "$test_dir/shunit2"
