#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source "$SCRIPT_DIR/../../shared-bash.sh"

. "$SCRIPT_DIR/requirements-install-prod.sh"
. "$SCRIPT_DIR/requirements-install-dev.sh"
