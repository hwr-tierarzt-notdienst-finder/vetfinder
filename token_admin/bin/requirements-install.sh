#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"

original_path="$(pwd)"
cd "$SCRIPT_DIR/.." || exit

requirements_abs_path=$(realpath "./requirements.txt")
echo_information "Installing python requirements from '$requirements_abs_path'"
echo_and_run ".venv/bin/python -m pip install -r requirements.txt"
echo_success "Installed python requirements from '$requirements_abs_path'"

cd "$original_path" || exit
