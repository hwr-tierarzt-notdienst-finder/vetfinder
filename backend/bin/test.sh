#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. "$SCRIPT_DIR/_python.sh"
. "$SCRIPT_DIR/_mongo.sh"

if [ "$(has_mongo_db_container 'test')" = 'true' ]; then
    echo_information "Removing existent mongo db test container"
    remove_mongo_container 'test'
fi

create_mongo_container 'test'

echo_and_run "PYTEST_DISABLE_PLUGIN_AUTOLOAD=true ENV=test $(venv_python_executable) -m pytest $SCRIPT_DIR/../tests $*"

remove_mongo_container 'test'