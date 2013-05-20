#!/bin/sh
# SKIP

#set -x

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"

#unset HOOK_VERBOSE_OPTION

setUp () {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
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


test_no_site_packages () {
    # See issue #102
    echo "" | mkvirtualenv "source" --no-site-packages >/dev/null 2>&1
    cpvirtualenv "source" "destination"
    ngsp_file="`sitepackages_dir`/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist in copied env" "[ -f \"$ngsp_file\" ]"
}


test_no_site_packages_default_behavior () {
    # See issue #102
    # virtualenv 1.7 changed to make --no-site-packages the default
    echo "" | mkvirtualenv "source" >/dev/null 2>&1
    cpvirtualenv "source" "destination"
    ngsp_file="`sitepackages_dir`/../no-global-site-packages.txt"
    assertTrue "$ngsp_file does not exist in copied env" "[ -f \"$ngsp_file\" ]"
}

. "$test_dir/shunit2"

