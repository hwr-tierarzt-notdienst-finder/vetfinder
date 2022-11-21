#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../.env"
LOCAL_ENV_FILE="$SCRIPT_DIR/../.env.local"
SECRETS_ENV_FILE="$SCRIPT_DIR/../.env.secret"
if [ -f "$LOCAL_ENV_FILE" ]; then
    . "$LOCAL_ENV_FILE"
fi
if [ -f "$SECRETS_ENV_FILE" ]; then
    . "$SECRETS_ENV_FILE"
fi