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
    unset VIRTUALENVWRAPPER_INITIALIZED
}

test_virtualenvwrapper_initialize() {
    assertTrue "Initialized" virtualenvwrapper_initialize
    for hook in premkvirtualenv postmkvirtualenv prermvirtualenv postrmvirtualenv preactivate postactivate predeactivate postdeactivate
    do
        assertTrue "Global $WORKON_HOME/$hook was not created" "[ -f $WORKON_HOME/$hook ]"
        assertTrue "Global $WORKON_HOME/$hook is not executable" "[ -x $WORKON_HOME/$hook ]"
    done
    assertTrue "Log file was not created" "[ -f $WORKON_HOME/hook.log ]"
    export pre_test_dir=$(cd "$test_dir"; pwd)
    echo "echo GLOBAL initialize >> \"$pre_test_dir/catch_output\"" >> "$WORKON_HOME/initialize"
    virtualenvwrapper_initialize
    output=$(cat "$test_dir/catch_output")
    expected="GLOBAL initialize"
    assertSame "$expected" "$output"
}

test_virtualenvwrapper_space_in_workon_home() {
    before="$WORKON_HOME"
    export WORKON_HOME="$WORKON_HOME/this has spaces"
 	expected="$WORKON_HOME"
    mkdir -p "$expected"
    virtualenvwrapper_initialize
    RC=$?
    assertSame "$expected" "$WORKON_HOME"
    assertSame "0" "$RC"
    export WORKON_HOME="$before"
}

test_virtualenvwrapper_verify_workon_home() {
    assertTrue "WORKON_HOME not verified" virtualenvwrapper_verify_workon_home
}

test_virtualenvwrapper_verify_workon_home_missing_dir() {
    old_home="$WORKON_HOME"
    WORKON_HOME="$WORKON_HOME/not_there"
    assertTrue "Directory already exists" "[ ! -d \"$WORKON_HOME\" ]"
    virtualenvwrapper_verify_workon_home >"$old_home/output" 2>&1
    output=$(cat "$old_home/output")
    assertSame "NOTE: Virtual environments directory $WORKON_HOME does not exist. Creating..." "$output"
    WORKON_HOME="$old_home"
}

test_virtualenvwrapper_verify_workon_home_missing_dir_quiet() {
    old_home="$WORKON_HOME"
    WORKON_HOME="$WORKON_HOME/not_there_quiet"
    assertTrue "Directory already exists" "[ ! -d \"$WORKON_HOME\" ]"
    output=$(virtualenvwrapper_verify_workon_home -q 2>&1)
    assertSame "" "$output"
    WORKON_HOME="$old_home"
}

test_virtualenvwrapper_verify_workon_home_missing_dir_grep_options() {
    old_home="$WORKON_HOME"
    WORKON_HOME="$WORKON_HOME/not_there"
    # This should prevent the message from being found if it isn't
    # unset correctly.
    export GREP_OPTIONS="--count"
    assertTrue "WORKON_HOME not verified" virtualenvwrapper_verify_workon_home
    WORKON_HOME="$old_home"
    unset GREP_OPTIONS
}

test_python_interpreter_set_incorrectly() {
    return_to="$(pwd)"
    cd "$WORKON_HOME"
    mkvirtualenv no_wrappers
    expected="ImportError: No module named virtualenvwrapper.hook_loader"
    # test_shell is set by tests/run_tests
    if [ "$test_shell" = "" ]
    then
        export test_shell=$SHELL
    fi
    subshell_output=$(VIRTUALENVWRAPPER_PYTHON="$WORKON_HOME/no_wrappers/bin/python" $test_shell $return_to/virtualenvwrapper.sh 2>&1)
    #echo "$subshell_output"
    echo "$subshell_output" | grep -q "$expected" 2>&1
    found_it=$?
    #echo "$found_it"
    assertTrue "Expected \'$expected\', got: \'$subshell_output\'" "[ $found_it -eq 0 ]"
    assertFalse "Failed to detect invalid Python location" "VIRTUALENVWRAPPER_PYTHON=$VIRTUAL_ENV/bin/python $SHELL $return_to/virtualenvwrapper.sh >/dev/null 2>&1"
    cd "$return_to"
    deactivate
}

. "$test_dir/shunit2"
