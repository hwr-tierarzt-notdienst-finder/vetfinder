#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
VENV_PATH="$SCRIPT_DIR/../.venv"

. "$SCRIPT_DIR/../../shared-bash.sh"
. "$SCRIPT_DIR/_python.sh"

function setup() {
    check_running_correct_python_version
    if [ ! -d "$VENV_PATH" ]; then
        create_venv
        install_package_management_tools
        . "$SCRIPT_DIR/requirements-install.sh"
    fi

    activate_venv
}

function check_running_correct_python_version() {
    local expected_version
    local python_version_file="$SCRIPT_DIR/../.python-version-match"
    expected_version="$(cat "$python_version_file")"
    local cli_version_str
    cli_version_str="$(python --version)"
    local actual_version="${cli_version_str#Python }"

    local expected_version_arr
    IFS='.' read -r -a expected_version_arr <<< "$expected_version"
    local actual_version_arr
    IFS='.' read -r -a actual_version_arr <<< "$actual_version"

    for (( i=0; i<"${#expected_version_arr[@]}"; i++ )) {
        if [ "${expected_version_arr[$i]}" != "${actual_version_arr[$i]}" ]; then
            throw "Wrong python version $actual_version does not match expected version $expected_version from $(realpath "$python_version_file")"
        fi
    }
}

function create_venv() {
    local abs_venv_path
    abs_venv_path=$(realpath "$VENV_PATH")

    echo_information "Creating python virtual environment at '$abs_venv_path'"
    echo_and_run_python "-m venv $VENV_PATH"
    if [ -d "$VENV_PATH" ]; then
        echo_success "Created python virtual environment at '$abs_venv_path'"
    else
        throw "Failed to create python virtual environment at '$abs_venv_path'"
    fi
}

function activate_venv() {
    echo_information "Activating python from virtual env"
    echo_and_run ". .venv/bin/activate"
    unset PS1
    echo_success "Activated python virtualenv"
    echo_information "Now using python version $(python --version) at $(which python)"
}

function install_package_management_tools() {
    echo_information "Installing pip-tools for python package management https://pypi.org/project/pip-tools/"
    echo_and_run_python '-m pip install pip-tools'
    echo_success "Installed pip-tools"
}

setup