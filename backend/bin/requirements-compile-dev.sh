#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"

requirements_abs_path=$(realpath "$SCRIPT_DIR/../requirements-dev.txt")
echo_information "Compiling development python requirements into '$requirements_abs_path'"
echo_and_run "pip-compile $SCRIPT_DIR/../requirements-dev.in --output-file $SCRIPT_DIR/../requirements-dev.txt"
echo_success "Compiled development python requirements into '$requirements_abs_path'"