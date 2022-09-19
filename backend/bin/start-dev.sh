#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SRC_DIR="$(realpath "$SCRIPT_DIR/../src")"

. "$SCRIPT_DIR/../../shared-bash.sh"
. "$SCRIPT_DIR/_python.sh"

echo_information "Setting up secrets"
echo_and_run "ENV=dev PYTHONPATH=${SRC_DIR} $(venv_python_executable) ${SRC_DIR}/entrypoints/setup_secrets.py"

echo_information "Starting app"
echo_and_run "ENV=dev PYTHONPATH=${SRC_DIR} . ${SRC_DIR}/entrypoints/app.sh"
