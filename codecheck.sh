#!/usr/bin/env bash

# Format code with Black
black .

# Check + fix linting with Ruff
ruff check . --fix

# Run full type check
mypy .
