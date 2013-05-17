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

test_create() {
    mkvirtualenv "env1" >/dev/null 2>&1
    assertTrue "Environment directory was not created" "[ -d $WORKON_HOME/env1 ]"
    for hook in postactivate predeactivate postdeactivate
    do
        assertTrue "env1 $hook was not created" "[ -f $WORKON_HOME/env1/bin/$hook ]"
        assertTrue "env1 $hook is not executable" "[ -x $WORKON_HOME/env1/bin/$hook ]"
    done
}

test_activates () {
    mkvirtualenv "env2" >/dev/null 2>&1
    assertTrue virtualenvwrapper_verify_active_environment
    assertSame "env2" $(basename "$VIRTUAL_ENV")
}

test_hooks () {
    export pre_test_dir=$(cd "$test_dir"; pwd)

    echo "#!/bin/sh" > "$WORKON_HOME/premkvirtualenv"
    echo "echo GLOBAL premkvirtualenv \`pwd\` \"\$@\" >> \"$pre_test_dir/catch_output\"" >> "$WORKON_HOME/premkvirtualenv"
    chmod +x "$WORKON_HOME/premkvirtualenv"

    echo "echo GLOBAL postmkvirtualenv >> $test_dir/catch_output" > "$WORKON_HOME/postmkvirtualenv"
    mkvirtualenv "env3" >/dev/null 2>&1
    output=$(cat "$test_dir/catch_output")
    workon_home_as_pwd=$(cd $WORKON_HOME; pwd)
    expected="GLOBAL premkvirtualenv $workon_home_as_pwd env3
GLOBAL postmkvirtualenv"
    assertSame "$expected" "$output"
    rm -f "$WORKON_HOME/premkvirtualenv"
    rm -f "$WORKON_HOME/postmkvirtualenv"
    deactivate
    rmvirtualenv "env3"
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
    assertSame "$RC" "1"
}

test_no_args () {
    mkvirtualenv 2>/dev/null 1>&2
    RC=$?
    assertSame "2" "$RC"
}

test_no_workon_home () {
    old_home="$WORKON_HOME"
    export WORKON_HOME="$WORKON_HOME/not_there"
    mkvirtualenv should_be_created >"$old_home/output" 2>&1
    output=$(cat "$old_home/output")
    assertTrue "Did not see expected message in \"$output\"" "cat \"$old_home/output\" | grep 'does not exist'"
    assertTrue "Did not create environment" "[ -d \"$WORKON_HOME/should_be_created\" ]"
    WORKON_HOME="$old_home"
}

test_mkvirtualenv_sitepackages () {
    # This part of the test is not reliable because
    # creating a new virtualenv from inside the
    # tox virtualenv inherits the setting from there.
#     # Without the option, verify that site-packages are copied.
# 	mkvirtualenv "with_sp" >/dev/null 2>&1
#     ngsp_file="`virtualenvwrapper_get_site_packages_dir`/../no-global-site-packages.txt"
#     assertFalse "$ngsp_file exists" "[ -f \"$ngsp_file\" ]"
#     rmvirtualenv "env3"
    
    # With the argument, verify that they are not copied.
    mkvirtualenv --no-site-packages "without_sp" >/dev/null 2>&1
    ngsp_file="`virtualenvwrapper_get_site_packages_dir`/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist" "[ -f \"$ngsp_file\" ]"
    rmvirtualenv "env4"
}

test_mkvirtualenv_args () {
    # See issue #102
    VIRTUALENVWRAPPER_VIRTUALENV_ARGS="--no-site-packages"
    # With the argument, verify that they are not copied.
    mkvirtualenv "without_sp2" >/dev/null 2>&1
    ngsp_file="`virtualenvwrapper_get_site_packages_dir`/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist" "[ -f \"$ngsp_file\" ]"
    rmvirtualenv "env4"
    unset VIRTUALENVWRAPPER_VIRTUALENV_ARGS
}

test_virtualenv_fails () {
    # Test to reproduce the conditions in issue #76
    # https://bitbucket.org/dhellmann/virtualenvwrapper/issue/76/
    # 
    # Should not run the premkvirtualenv or postmkvirtualenv hooks
    # because the environment is not created and even the
    # premkvirtualenv hooks are run *after* the environment exists
    # (but before it is activated).
    export pre_test_dir=$(cd "$test_dir"; pwd)

    VIRTUALENVWRAPPER_VIRTUALENV=false

    echo "#!/bin/sh" > "$WORKON_HOME/premkvirtualenv"
    echo "echo GLOBAL premkvirtualenv \`pwd\` \"\$@\" >> \"$pre_test_dir/catch_output\"" >> "$WORKON_HOME/premkvirtualenv"
    chmod +x "$WORKON_HOME/premkvirtualenv"

    echo "echo GLOBAL postmkvirtualenv >> $test_dir/catch_output" > "$WORKON_HOME/postmkvirtualenv"
    mkvirtualenv "env3" >/dev/null 2>&1
    output=$(cat "$test_dir/catch_output" 2>/dev/null)
    workon_home_as_pwd=$(cd $WORKON_HOME; pwd)
    expected=""
    assertSame "$expected" "$output"
    rm -f "$WORKON_HOME/premkvirtualenv"
    rm -f "$WORKON_HOME/postmkvirtualenv"

    VIRTUALENVWRAPPER_VIRTUALENV=virtualenv
}


. "$test_dir/shunit2"
