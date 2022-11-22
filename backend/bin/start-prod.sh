#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$(realpath "$SCRIPT_DIR/../..")
BACKEND_DIR="$ROOT_DIR/backend"

. "$SCRIPT_DIR/mongo-start-prod-container.sh"
. "$SCRIPT_DIR/_load_dotenv_vars.sh"

run_detached=0
while test $# != 0
do
    case "$1" in
    --run-detached)
        run_detached=1;;
    esac
    shift
done

temp_dir="$SCRIPT_DIR/../temp_dir_for_copy_to_docker_prod"
echo_information "Creating temporary directory '$temp_dir' with files that will be copied to the production container"
mkdir -p "$temp_dir"
cp "$ROOT_DIR/shared-bash.sh" "$temp_dir/shared-bash.sh"
mkdir -p "$temp_dir/backend"
cp "$BACKEND_DIR/.env" "$temp_dir/backend/.env"
if [ -f "$BACKEND_DIR/.env.local" ]; then
    cp "$BACKEND_DIR/.env.local" "$temp_dir/backend/.env.local"
fi
if [ -f "$BACKEND_DIR/.env.secret" ]; then
    cp "$BACKEND_DIR/.env.secret" "$temp_dir/backend/.env.secret"
fi
cp "$BACKEND_DIR/.gitignore" "$temp_dir/backend/.gitignore"
cp "$BACKEND_DIR/requirements.txt" "$temp_dir/backend/requirements.txt"
cp -rL "$BACKEND_DIR/secrets" "$temp_dir/backend/secrets"
cp -r "$BACKEND_DIR/src" "$temp_dir/backend/src"

echo_information "Building docker image for app"
echo_and_run "docker build -f $BACKEND_DIR/app.prod.Dockerfile -t tierarzt_notdienst_app_prod --no-cache $temp_dir"

echo_information "Removing temporary directory '$temp_dir'"
echo_and_run "rm -rf $temp_dir"

if [ $run_detached = 1 ]; then
    extra_options=' --detach'
else
    extra_options=''
fi

echo_information "Running app as docker container"
echo_and_run "docker run --name tierarzt_notdienst_app_prod -v $BACKEND_DIR/logs:/app/backend/logs --net=host ${extra_options} tierarzt_notdienst_app_prod"
