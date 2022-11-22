#!/bin/bash

ENTRYPOINTS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$ENTRYPOINTS_DIR/.." || exit 1

# Load environment variables from .env files
. ../.env
if [ -f ../.env.secret ]; then
    . ../.env.secret
fi
if [ -f ../.env.local ]; then
    . ../.env.local
fi

options=()
if [ "$ENV" = 'prod' ]; then
    options+=('--host' '0.0.0.0')
else
    options+=('--host' '127.0.0.1')
fi

if [ "$ENV" = 'dev' ]; then
    options+=('--reload')
fi

uvicorn app:app ${options[*]} --port "$(eval echo \$\{FASTAPI_"${ENV^^}"_PORT\})"
