#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/_mongo.sh"

# TODO: Create needs to be renamed to start
create_mongo_container "prod"
