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

if [ "$ENV" = 'dev' ]; then
    uvicorn app:app --port "$(eval echo \$\{FASTAPI_"${ENV^^}"_PORT\})" --reload
else
    uvicorn app:app --port "$(eval echo \$\{FASTAPI_"${ENV^^}"_PORT\})"
fi
