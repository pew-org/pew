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
    mkvirtualenv -a "$project" "$env" >/dev/null 2>&1
    assertTrue ".project not found" "[ -f $ptrfile ]"
    assertEquals "$ptrfile contains wrong content" "$project" "$(cat $ptrfile)"
}

test_preactivate() {
    project="/dev/null"
    env="env2"
    ptrfile="$WORKON_HOME/$env/.project"
	cat - >"$WORKON_HOME/preactivate" <<EOF
#!/bin/sh
if [ -f "$ptrfile" ]
then
    echo exists >> "$test_dir/catch_output"
else
    echo noexists >> "$test_dir/catch_output"
fi
EOF
    chmod +x "$WORKON_HOME/preactivate"
    mkvirtualenv -a "$project" "$env" >/dev/null 2>&1
	assertSame "preactivate did not find file" "exists" "$(cat $test_dir/catch_output)"
}

test_postactivate() {
    project="/dev/null"
    env="env3"
    ptrfile="$WORKON_HOME/$env/.project"
cat - >"$WORKON_HOME/postactivate" <<EOF
#!/bin/sh
if [ -f "$ptrfile" ]
then
    echo exists >> "$test_dir/catch_output"
else
    echo noexists >> "$test_dir/catch_output"
fi
EOF
    chmod +x "$WORKON_HOME/postactivate"
    mkvirtualenv -a "$project" "$env" >/dev/null 2>&1
	assertSame "postactivate did not find file" "exists" "$(cat $test_dir/catch_output)"
}

. "$test_dir/shunit2"
