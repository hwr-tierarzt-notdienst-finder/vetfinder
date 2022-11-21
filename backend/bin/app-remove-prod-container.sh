#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"

container_name="tierarzt_notdienst_app_prod"

container_id=$(docker ps -aqf "name=^$container_name")

if [ -z "$container_id" ]; then
    throw "Could not find container with name=$container_name"
else
    echo_information "Found mongo db container id=$container_id from name=$container_name"
fi

echo "Stopping container with id=$container_id"
echo_and_run "docker stop $container_id"

echo_information "Removing container with id=$container_id"
echo_and_run "docker container rm $container_id"