#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"

original_path="$(pwd)"
cd "$SCRIPT_DIR/.." || exit

function echo_and_run_venv_python() {
    echo_processing "Running: .venv/bin/python ${*}"

    "${SCRIPT_DIR}/../.venv/bin/python" "$@"
}

echo_information "Upgrading pip"
echo_and_run_venv_python -m pip install --upgrade pip
echo_success "Upgraded pip"

echo_information "Installing pip-tools"
echo_and_run_venv_python -m pip install pip-tools
echo_success "Installed pip-tools"

echo_information "Compiling production python requirements into requirements.txt"
echo_and_run "${SCRIPT_DIR}/../.venv/bin/pip-compile requirements.in --output-file requirements.txt"
echo_success "Compiled production python requirements into requirements.txt"

echo_information "Compiling development python requirements into requirements-dev.txt"
echo_and_run "${SCRIPT_DIR}/../.venv/bin/pip-compile requirements-dev.in --output-file requirements-dev.txt"
echo_success "Compiled development python requirements into requirements-dev.txt"

cd "$original_path" || exit
