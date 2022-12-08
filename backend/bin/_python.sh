#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"
. "$SCRIPT_DIR/_load_dotenv_vars.sh"

function python_executable() {
    if [ -z "${PYTHON_EXECUTABLE:-}" ]; then
        echo "python3.10"
    else
        echo "$PYTHON_EXECUTABLE"
    fi
}

function venv_python_executable() {
    echo "$(realpath "$SCRIPT_DIR/..")/.venv/bin/python"
}

function echo_and_run_python() {
    echo_and_run "$(python_executable) $*"
}

function run_python() {
    eval "$(python_executable) $*"
}

function echo_and_run_venv_python() {
    echo_and_run "$(venv_python_executable) $*"
}

function run_venv_python() {
    eval "$(venv_python_executable) $*"
}