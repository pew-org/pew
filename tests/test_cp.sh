#!/bin/sh

#set -x

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"

#unset HOOK_VERBOSE_OPTION

setUp () {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    source "$test_dir/../virtualenvwrapper.sh"
    rm -f "$test_dir/catch_output"
    echo
}

tearDown() {
    if type deactivate >/dev/null 2>&1
    then 
        deactivate
    fi
    rm -rf "$WORKON_HOME"
}

test_new_env_activated () {
    mkvirtualenv "source"
    (cd tests/testpackage && python setup.py install) >/dev/null 2>&1
    cpvirtualenv "source" "destination"
    rmvirtualenv "source"
    testscript="$(which testscript.py)"
    assertTrue "Environment test script not found in path" "[ $WORKON_HOME/destination/bin/testscript.py -ef $testscript ]"
    testscriptcontent="$(cat $testscript)"
    assertTrue "No cpvirtualenvtest in $testscriptcontent" "echo $testscriptcontent | grep cpvirtualenvtest"
    assertTrue virtualenvwrapper_verify_active_environment
}

test_virtual_env_variable () {
    mkvirtualenv "source"
    cpvirtualenv "source" "destination"
    assertSame "Wrong virtualenv name" "destination" $(basename "$VIRTUAL_ENV")
    assertTrue "$WORKON_HOME not in $VIRTUAL_ENV" "echo $VIRTUAL_ENV | grep -q $WORKON_HOME"
}

fake_virtualenv () {
    typeset envname="$1"
    touch "$envname/fake_virtualenv_was_here"
    virtualenv $@
}

test_virtualenvwrapper_virtualenv_variable () {
    mkvirtualenv "source"
    export VIRTUALENVWRAPPER_VIRTUALENV=fake_virtualenv
    cpvirtualenv "source" "destination"
    unset VIRTUALENVWRAPPER_VIRTUALENV
    assertTrue "wrapper was not run" "[ -f $VIRTUAL_ENV/fake_virtualenv_was_here ]"
}

test_source_relocatable () {
    mkvirtualenv "source"
    (cd tests/testpackage && python setup.py install) >/dev/null 2>&1
    assertTrue "virtualenv --relocatable \"$WORKON_HOME/source\""
    cpvirtualenv "source" "destination"
    testscript="$(which testscript.py)"
    assertTrue "Environment test script not the same as copy" "[ $WORKON_HOME/destination/bin/testscript.py -ef $testscript ]"
    assertTrue virtualenvwrapper_verify_active_environment
    assertSame "Wrong virtualenv name" "destination" $(basename "$VIRTUAL_ENV")
}

test_source_does_not_exist () {
    out="$(cpvirtualenv virtualenvthatdoesntexist foo)"
    assertSame "$out" "virtualenvthatdoesntexist virtualenv doesn't exist"
}

test_hooks () {
    mkvirtualenv "source"

    export pre_test_dir=$(cd "$test_dir"; pwd)

    # Set the interpreter of the hook script to the simple shell
    echo "#!/bin/sh" > "$WORKON_HOME/premkvirtualenv"
    echo "echo GLOBAL premkvirtualenv \`pwd\` \"\$@\" >> \"$pre_test_dir/catch_output\"" >> "$WORKON_HOME/premkvirtualenv"
    chmod +x "$WORKON_HOME/premkvirtualenv"

    echo "echo GLOBAL postmkvirtualenv >> $test_dir/catch_output" > "$WORKON_HOME/postmkvirtualenv"

    # Set the interpreter of the hook script to the simple shell
    echo "#!/bin/sh" > "$WORKON_HOME/precpvirtualenv"
    echo "echo GLOBAL precpvirtualenv \`pwd\` \"\$@\" >> \"$pre_test_dir/catch_output\"" >> "$WORKON_HOME/precpvirtualenv"
    chmod +x "$WORKON_HOME/precpvirtualenv"

    # Set the interpreter of the hook script to the simple shell
    echo "#!/bin/sh" > "$WORKON_HOME/postcpvirtualenv"
    echo "echo GLOBAL postcpvirtualenv >> $test_dir/catch_output" > "$WORKON_HOME/postcpvirtualenv"

    cpvirtualenv "source" "destination"

    output=$(cat "$test_dir/catch_output")
    workon_home_as_pwd=$(cd $WORKON_HOME; pwd)

    expected="GLOBAL precpvirtualenv $workon_home_as_pwd source destination
GLOBAL premkvirtualenv $workon_home_as_pwd destination
GLOBAL postmkvirtualenv
GLOBAL postcpvirtualenv"

    assertSame "$expected" "$output"

    rm -f "$WORKON_HOME/premkvirtualenv"
    rm -f "$WORKON_HOME/postmkvirtualenv"
}

test_no_site_packages () {
    # See issue #102
    mkvirtualenv "source" --no-site-packages >/dev/null 2>&1
    cpvirtualenv "source" "destination"
    ngsp_file="`virtualenvwrapper_get_site_packages_dir`/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist in copied env" "[ -f \"$ngsp_file\" ]"
}

test_no_site_packages_default_args () {
    # See issue #102
    VIRTUALENVWRAPPER_VIRTUALENV_ARGS="--no-site-packages"
    # With the argument, verify that they are not copied.
    mkvirtualenv "source" >/dev/null 2>&1
    cpvirtualenv "source" "destination"
    ngsp_file="`virtualenvwrapper_get_site_packages_dir`/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist" "[ -f \"$ngsp_file\" ]"
    unset VIRTUALENVWRAPPER_VIRTUALENV_ARGS
}

test_no_site_packages_default_behavior () {
    # See issue #102
    # virtualenv 1.7 changed to make --no-site-packages the default
    mkvirtualenv "source" >/dev/null 2>&1
    cpvirtualenv "source" "destination"
    ngsp_file="`virtualenvwrapper_get_site_packages_dir`/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist in copied env" "[ -f \"$ngsp_file\" ]"
}

. "$test_dir/shunit2"

