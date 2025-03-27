#!/bin/bash

# Find the Python interpreter with pytest installed
PYTHON_PATH=$(which python3)

# Run the tests
$PYTHON_PATH -m pytest -v "$@"
