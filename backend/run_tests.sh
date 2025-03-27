#!/bin/bash

# Find the Python interpreter with pytest installed
PYTHON_PATH=$(which python3)

# Make sure pytest is installed
if ! $PYTHON_PATH -c "import pytest" &> /dev/null; then
    echo "pytest not found. Installing..."
    $PYTHON_PATH -m pip install pytest pytest-flask
fi

# Run the tests
$PYTHON_PATH -m pytest -v "$@"
