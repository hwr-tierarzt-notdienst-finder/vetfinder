#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"

skip_if_container_does_not_exist=0
while test $# != 0
do
    case "$1" in
    --skip-if-container-does-not-exist)
        skip_if_container_does_not_exist=1;;
    esac
    shift
done

container_name="tierarzt_notdienst_app_prod"

container_id=$(docker ps -aqf "name=^$container_name")

if [ -z "$container_id" ]; then
    if [ $skip_if_container_does_not_exist = 1 ]; then
        echo_information "Container does not exist, skipping!"
        exit 0
    else
        throw "Could not find container with name=$container_name"
    fi
else
    echo_information "Found mongo db container id=$container_id from name=$container_name"
fi

echo "Stopping container with id=$container_id"
echo_and_run "docker stop $container_id"

echo_information "Removing container with id=$container_id"
echo_and_run "docker container rm $container_id"