#!/bin/bash

# Exit on error
set -o errexit

# Exit if tries to use undeclared variable
set -o nounset

function echo_token() {
    local token=$1

    if [ "$token" = "icon:processing" ]; then
        echo "⠧"
    elif [ "$token" = "icon:success" ]; then
        echo "✅"
    elif [ "$token" = "icon:failure" ]; then
        echo "❌"
    elif [ "$token" = "icon:information" ]; then
        echo "ℹ"
    else
        throw "Unknown token '$token' found"
    fi
}

_terminal_supports_escape_sequences="$(( $(tput colors 2>/dev/null || echo "0") >= 256 ))"
function check_terminal_supports_escape_sequences() {
    echo $_terminal_supports_escape_sequences
}

function echo_escape_sequence() {
    local sequence_name

    if [ "$(check_terminal_supports_escape_sequences)" != 1 ]; then
        echo ""
        exit 0
    fi

    sequence_name=$1

    if [ "$sequence_name" = "reset" ]; then
        echo -e "\e[0m"
    elif [ "$sequence_name" = "color:red" ] || [ "$sequence_name" = "color:failure" ] || [ "$sequence_name" = "red" ]; then
        echo -e "\e[31m"
    elif [ "$sequence_name" = "color:green" ] || [ "$sequence_name" = "color:success" ] || [ "$sequence_name" = "green" ]; then
        echo -e "\e[32m"
    elif [ "$sequence_name" = "color:blue" ] || [ "$sequence_name" = "color:processing" ] || [ "$sequence_name" = "blue" ]; then
        echo -e "\e[34m"
    elif [ "$sequence_name" = "modifier:bold" ] || [ "$sequence_name" = "bold" ]; then
        echo -e "\e[1m"
    elif [ "$sequence_name" = "modifier:underlined" ] || [ "$sequence_name" = "bold" ]; then
        echo -e "\e[1m"
    else
        throw "Unknown escape sequence '$sequence_name'"
    fi
}

function echo_escaped() {
    local args_except_last=("${@:1:$(($#-1))}")
    local last_arg="${*: -1}"

    local prefix=""
    for escape_sequence in "${args_except_last[@]}"; do
        prefix="${prefix}$(echo_escape_sequence "$escape_sequence")"
    done

    local suffix
    suffix="$(echo_escape_sequence "reset")"

    echo "${prefix}${last_arg}${suffix}"
}

function echo_colored() {
    local color=$1
    local str=$2

    echo_escaped "color:$color" "$str"
}

function echo_processing() {
    echo_colored "processing" "$(echo_token "icon:processing") $1"
}

function echo_success() {
    echo_colored "success" "$(echo_token "icon:success") $1"
}

function echo_failure() {
    echo_colored "failure" "$(echo_token "icon:failure") $1"
}

function echo_information() {
    echo "$(echo_token "icon:information") $1"
}

function echo_and_run() {
    local cmd=$1

    echo_processing "Running: $cmd"
    eval "$cmd"
}

function throw() {
    local err_msg=$1

    echo_failure "Error: $err_msg" 1>&2

    kill -SIGTERM "$$"
}
