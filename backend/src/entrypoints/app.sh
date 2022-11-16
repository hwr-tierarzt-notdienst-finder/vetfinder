#!/bin/bash

ENTRYPOINTS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$ENTRYPOINTS_DIR/.."

if [ "$ENV" = 'prod' ]; then
    uvicorn app:app
else
    uvicorn app:app --reload
fi
