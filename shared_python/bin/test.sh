#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SRC_DIR="$(realpath "$SCRIPT_DIR/../src")"

. "$SCRIPT_DIR/../../shared-bash.sh"

venv_python_executable="${SCRIPT_DIR}/../.venv/bin/python"

echo_information "Running tests"
echo_and_run "ENV=test PYTHONPATH=${SRC_DIR} PYTEST_DISABLE_PLUGIN_AUTOLOAD=true $venv_python_executable -m pytest $SCRIPT_DIR/../tests $*"
