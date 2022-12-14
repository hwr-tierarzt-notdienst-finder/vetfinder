#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
. "$SCRIPT_DIR/_python.sh"

requirements_abs_path=$(realpath "$SCRIPT_DIR/../requirements.txt")
echo_information "Installing production python requirements in '$requirements_abs_path'"
echo_and_run_venv_python "-m pip install -r $SCRIPT_DIR/../requirements.txt"
echo_success "Installed production requirements in '$requirements_abs_path'"
