#!/bin/bash

# Usage: source ./setup-development-environment.source

# Check if the script is being sourced
(return 0 2>/dev/null) || {
    echo "This script should be sourced, not executed."
    exit 1
}

if command -v python3 &>/dev/null; then
    echo "Python3 is installed"
    command -v python3
    python3 --version
else
    update-linux.sh
fi

# Check if the virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    python3 -m venv venv
    source ./venv/bin/activate
else
    echo "Virtual environment is active: $VIRTUAL_ENV"
fi

requirements_file="requirements.txt"
if [[ -s "$requirements_file" ]]; then
    python3 -m pip install -r requirements.txt
else
    install-python-package gspread
    install-python-package libcst
    install-python-package pandas
    install-python-package pandas-stubs
    install-python-package pip-check-reqs
    install-python-package pipdeptree
    install-python-package pytest
    install-python-package SQLAlchemy
    install-python-package sqlalchemy-stubs
    install-python-package sqlacodegen_v2

    python3 -m pip freeze >requirements.txt
fi

python3 -m pip list --outdated

# python3 -m pip-check-reqs

# python3 -m pipdeptree

echo "Remember to deactivate before running this script again!"
