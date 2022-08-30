#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"
. "$SCRIPT_DIR/../.env"


function remove_container() {
    local container_id
    container_id=$(docker ps -aqf "name=^${MONGO_CONTAINER_NAME}$")

    if [ -z "$container_id" ]; then
        throw "Could not find container with name=$MONGO_CONTAINER_NAME"
    else
        echo_information "Found mongo db container id=$container_id from name=$MONGO_CONTAINER_NAME"
    fi

    echo "Stopping container with id=$container_id"
    echo_and_run "docker stop $container_id"

    echo_information "Removing container with id=$container_id"
    echo_and_run "docker container rm $container_id"
}

remove_container