#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"
. "$SCRIPT_DIR/../.env"


function create_container() {
    local db_dir_abs_path
    db_dir_abs_path="$(realpath "$SCRIPT_DIR/../$MONGO_DB_DIR")"

    echo_information "Creating mongo db container"
    echo_and_run "docker run --name $MONGO_CONTAINER_NAME -d -e MONGO_INITDB_ROOT_USERNAME=$MONGO_DEV_INITDB_ROOT_USERNAME -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_DEV_INITDB_ROOT_PASSWORD -p $MONGO_HOST_PORT:27017 -v $db_dir_abs_path:/data/db mongo:$MONGO_VERSION"
}

create_container