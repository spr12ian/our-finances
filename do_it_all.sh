#!/usr/bin/env bash

# Check if DEBUG is set to true
if [ "$DEBUG" = "true" ]; then
    set -x # Enable debugging
else
    set +x # Disable debugging
fi

stop_if_module_has_errors() {
    module=$1
    echo "make ${module}"
    make "${module}"
    log_file="${module}.log"
    if [ -f "${log_file}" ]; then
        cat "${log_file}"
    fi
    error_file="${module}_error.log"
    if [ -f "${error_file}" ]; then
        echo "Check ${error_file}"
        exit 1
    fi
}

stop_if_module_has_errors key_check

stop_if_module_has_errors analyze_spreadsheet

stop_if_module_has_errors google_sheets_to_sqlite

db_filename="our_finances.sqlite"

if [ -f "${db_filename}" ]; then
    stop_if_module_has_errors vacuum_sqlite_database

    stop_if_module_has_errors generate_reports

    sqlitebrowser "${db_filename}" &

    stop_if_module_has_errors first_normal_form

    stop_if_module_has_errors execute_sqlite_queries

    stop_if_module_has_errors generate_sqlalchemy_models

    stop_if_module_has_errors execute_sqlalchemy_queries
fi
