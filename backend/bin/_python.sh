. "$SCRIPT_DIR/../../shared-bash.sh"
if [ -f "$SCRIPT_DIR/../.env.local" ]; then
    . "$SCRIPT_DIR/../.env.local"
fi

function python_executable() {
    if [ -z "$PYTHON_EXECUTABLE" ]; then
        echo "python"
    else
        echo "$PYTHON_EXECUTABLE"
    fi
}

function echo_and_run_python() {
    echo_and_run "$(python_executable) $*"
}

function run_python() {
    eval "$(python_executable) $*"
}