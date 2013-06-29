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
    echo "#!/bin/sh" > "$WORKON_HOME/preactivate"
    echo "#!/bin/sh" > "$WORKON_HOME/postactivate"
}

test_associate() {
    project="/dev/null"
    env="env1"
    ptrfile="$WORKON_HOME/$env/.project"
    echo "" | pew-new -a "$project" "$env" >/dev/null
    assertTrue ".project not found" "[ -f $ptrfile ]"
    assertEquals "$ptrfile contains wrong content" "$project" "$(cat $ptrfile)"
}


. "$test_dir/shunit2"
