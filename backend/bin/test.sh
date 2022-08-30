#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

PYTEST_DISABLE_PLUGIN_AUTOLOAD=true python3 -m pytest "$SCRIPT_DIR/../tests" "$@"
