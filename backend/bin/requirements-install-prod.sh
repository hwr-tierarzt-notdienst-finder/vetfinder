#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

requirements_abs_path=$(realpath "$SCRIPT_DIR/../requirements.txt")
echo_information "Installing production python requirements in '$requirements_abs_path'"
echo_and_run "python3 -m pip install -r $SCRIPT_DIR/../requirements.txt"
echo_success "Installed production requirements in '$requirements_abs_path'"
