#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"


FORM_WEBSITE_DIR="$( realpath "$SCRIPT_DIR/.." )"
DOCKER_FILE_NAME="prod.Dockerfile"
CONTAINER_NAME="tierarzt_notdienst_form_website"
HOST_HTTP_PORT=81
CONTAINER_HTTP_PORT=3000


function remove_old_container_if_exists() {
    container_id=$(docker ps -aqf "name=^$CONTAINER_NAME")
    if [ "$container_id" != "" ]; then
        echo_information "Stopping container with id=$container_id"
        echo_and_run "docker stop $container_id"

        echo_information "Removing container with id=$container_id"
        echo_and_run "docker container rm $container_id"
    else
        echo_information "No container with name=$CONTAINER_NAME found, skipping removal"
    fi
}

remove_old_container_if_exists

echo_information "Building docker image '$CONTAINER_NAME'"
echo_and_run "docker build -f $FORM_WEBSITE_DIR/$DOCKER_FILE_NAME -t $CONTAINER_NAME --no-cache $FORM_WEBSITE_DIR"

echo_information "Recreating form website docker container '$CONTAINER_NAME'"
echo_and_run "docker run --name $CONTAINER_NAME -p $HOST_HTTP_PORT:$CONTAINER_HTTP_PORT $CONTAINER_NAME --detach"
