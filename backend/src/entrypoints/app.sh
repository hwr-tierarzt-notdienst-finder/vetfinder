#!/bin/bash

ENTRYPOINTS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$ENTRYPOINTS_DIR/.."

uvicorn app:app --reload
