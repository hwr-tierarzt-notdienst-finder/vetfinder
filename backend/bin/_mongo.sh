#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/../../shared-bash.sh"
. "$SCRIPT_DIR/../.env"


function is_env_context() {
    local arg=$1

    if [ "$arg" = 'prod' ] ||  [ "$arg" = 'dev' ] || [ "$arg" = 'test' ]; then
        echo "true"
    else
        echo "false"
    fi
}


function validate_env_context() {
    local env_context=$1

    if [ "$(is_env_context "$env_context")" = 'false' ]; then
        throw "Invalid environment context=$env_context"
    fi

    echo "$env_context"
}

function get_container_name_by_env_context() {
    local base_name
    local env_context
    base_name=$1
    env_context="$(validate_env_context "$2")"

    echo "${base_name}_$env_context"
}

function get_env_var_value() {
    local var_name_start
    local var_name_ending
    local env_context
    if [ "$#" -eq 1 ]; then
        var_name_start=''
        var_name_ending="$1"
        env_context=''
    elif [ "$#" -eq 2 ]; then
        if [ "$(is_env_context "$2")" = 'true' ]; then
            var_name_start=''
            var_name_ending="$1"
            env_context="$2"
        else
            var_name_start="$1_"
            var_name_ending="$2"
            env_context=''
        fi
    else
        var_name_start="$1_"
        var_name_ending="$2"
        env_context="$3"
    fi

    local var_name_middle
    if [ "$env_context" = '' ]; then
        var_name_middle=""
    else
        local env_context
        env_context="$(validate_env_context "$env_context")"

        if [ "$env_context" = 'prod' ]; then
            var_name_middle='PROD_'
        elif [ "$env_context" = 'dev' ]; then
            var_name_middle='DEV_'
        elif [ "$env_context" = 'test' ]; then
            var_name_middle='TEST_'
        else
            throw "Unexpected environment context=$env_context"
            exit 0
        fi
    fi

    eval "echo \$${var_name_start}${var_name_middle}${var_name_ending}"
}

function get_mongo_env_var_value() {
    if [ "$#" -eq 1 ]; then
        get_env_var_value 'MONGO' "$1"
    else
        get_env_var_value 'MONGO' "$1" "$2"
    fi
}

function get_mongo_container_name() {
    local env_context
    env_context="$(validate_env_context "$1")"

    get_container_name_by_env_context "$(get_mongo_env_var_value 'CONTAINER_BASE_NAME')" "$env_context"
}

function get_mongo_db_dir() {
    local env_context
    env_context="$(validate_env_context "$1")"

    local dbs_dir
    dbs_dir="$(get_mongo_env_var_value 'DBS_DIR')"

    realpath "$SCRIPT_DIR/../$dbs_dir/$env_context"
}

function create_mongo_container() {
    local env_context
    env_context="$1"

    local container_name
    container_name="$(get_mongo_container_name "$env_context")"

    local initdb_root_username
    initdb_root_username=$(get_mongo_env_var_value 'INITDB_ROOT_USERNAME' "$env_context")

    local initdb_root_password
    initdb_root_password=$(get_mongo_env_var_value 'INITDB_ROOT_PASSWORD' "$env_context")

    local host_port
    host_port=$(get_mongo_env_var_value 'HOST_PORT' "$env_context")

    local db_dir_abs_path
    db_dir_abs_path="$(get_mongo_db_dir "$env_context")"

    local version
    version="$(get_mongo_env_var_value 'VERSION')"

    echo_information "Creating mongo db container with name=$container_name"
    echo_and_run "docker run --name $container_name -d -e MONGO_INITDB_ROOT_USERNAME=$initdb_root_username -e MONGO_INITDB_ROOT_PASSWORD=$initdb_root_password -p $host_port:27017 -v $db_dir_abs_path:/data/db mongo:$version"
}

function remove_mongo_container() {
    local env_context
    env_context="$1"

    local container_name
    container_name="$(get_mongo_container_name "$env_context")"

    local container_id
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
}