#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"

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

requirements_abs_path=$(realpath "$SCRIPT_DIR/../requirements.txt")
requirements_dev_abs_path=$(realpath "$SCRIPT_DIR/../requirements-dev.txt")
echo_information "Installing python requirements from requirements.txt and requirements-dev.txt"
echo_and_run "${SCRIPT_DIR}/../.venv/bin/pip-sync $requirements_abs_path $requirements_dev_abs_path"
echo_success "Installed python requirements"