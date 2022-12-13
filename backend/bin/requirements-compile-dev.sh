#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"

original_path="$(pwd)"
cd "$SCRIPT_DIR/.." || exit

requirements_abs_path=$(realpath "./requirements-dev.txt")
echo_information "Compiling development python requirements into '$requirements_abs_path'"
echo_and_run "pip-compile requirements-dev.in --output-file requirements-dev.txt"
echo_success "Compiled development python requirements into '$requirements_abs_path'"

cd "$original_path" || exit
