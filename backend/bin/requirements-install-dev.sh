#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
. "$SCRIPT_DIR/_python.sh"

echo_information "Upgrading pip"
echo_and_run_venv_python -m pip install --upgrade pip
echo_success "Upgraded pip"

echo_information "Installing pip-tools"
echo_and_run_venv_python -m pip install pip-tools
echo_success "Installed pip-tools"

requirements_abs_path=$(realpath "$SCRIPT_DIR/../requirements-dev.txt")
echo_information "Installing development python requirements in '$requirements_abs_path'"
echo_and_run "${SCRIPT_DIR}/../.venv/bin/pip-sync $SCRIPT_DIR/../../shared_python/requirements-dev.txt $SCRIPT_DIR/../../shared_python/requirements.txt $SCRIPT_DIR/../requirements.txt $SCRIPT_DIR/../requirements-dev.txt"
echo_success "Installed development requirements in '$requirements_abs_path'"
