#!/bin/sh

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
	cd tests/testpackage
    echo "python setup.py install" | mkvirtualenv source >/dev/null 2>&1
    echo "" | cpvirtualenv "source" "destination"
    rmvirtualenv "source"
    testscript=$(echo "which testscript.py" | workon destination | tail -n1)
	echo $testscript
    assertTrue "Environment test script not found in path" "[ $WORKON_HOME/destination/bin/testscript.py -ef $testscript ]"
    testscriptcontent="$(cat $testscript)"
    assertTrue "No cpvirtualenvtest in $testscriptcontent" "echo $testscriptcontent | grep cpvirtualenvtest"
}

test_virtual_env_variable () {
    echo "" | mkvirtualenv "source"
	echo "" | cpvirtualenv "source" "destination"
    envname=$(echo "echo \$VIRTUAL_ENV" | workon destination | tail -n1)
    assertSame "Wrong virtualenv name" "destination" $(basename $envname)
    assertTrue "$WORKON_HOME not in $envname" "echo $envname | grep -q $WORKON_HOME"
}

test_source_relocatable () {
    cd tests/testpackage
    echo "python setup.py install" | mkvirtualenv source >/dev/null 2>&1
    assertTrue "virtualenv --relocatable \"$WORKON_HOME/source\""
    echo "" | cpvirtualenv "source" "destination"
    testscript=$(echo "which testscript.py" | workon destination | tail -n1)
    assertTrue "Environment test script not the same as copy" "[ $WORKON_HOME/destination/bin/testscript.py -ef $testscript ]"
    envname=$(echo "echo \$VIRTUAL_ENV" | workon destination | tail -n1)
    assertSame "Wrong virtualenv name" "destination" $(basename "$envname")
}

test_source_does_not_exist () {
    out="$(cpvirtualenv virtualenvthatdoesntexist foo 2>&1)"
    assertSame "$out" "Please provide a valid virtualenv to copy"
}


test_no_site_packages () {
    # See issue #102
    echo "" | mkvirtualenv "source" --no-site-packages >/dev/null 2>&1
	echo "" | cpvirtualenv "source" "destination"
    ngsp_file=$(echo "sitepackages_dir" | workon destination | tail -n1)"/../no-global-site-packages.txt"

    assertTrue "$ngsp_file does not exist in copied env" "[ -f \"$ngsp_file\" ]"
}

. "$test_dir/shunit2"

