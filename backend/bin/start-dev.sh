#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SRC_DIR="$(realpath "$SCRIPT_DIR/../src")"

. "$SCRIPT_DIR/../../shared-bash.sh"
. "$SCRIPT_DIR/_python.sh"

echo_information "Starting API"
echo_and_run "ENV=dev PYTHONPATH=${SRC_DIR} . ${SRC_DIR}/entrypoints/api.sh"
