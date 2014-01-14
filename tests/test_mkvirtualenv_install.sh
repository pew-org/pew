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
    rm -f "$test_dir/requirements.txt"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

# test_single_package () {
#     installed=$(echo "pip freeze" | pew-new -i IPy "env4" )
#     assertTrue "IPy not found in $installed" "echo $installed | grep IPy=="
# }

# test_multiple_packages () {
# 	echo "" | pew-new -i IPy -i WebTest "env5" >/dev/null 
#     installed=$(echo "pip freeze" | pew-workon env5 )
#     assertTrue "IPy not found in $installed" "echo $installed | grep IPy=="
#     assertTrue "WebTest not found in $installed" "echo $installed | grep WebTest=="
#}

. "$test_dir/shunit2"
