#!/bin/bash

VENV_DIR=".venv"

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Install dependencies using the venv's pip
"$VENV_DIR/bin/pip" install -r requirements.txt

# Run the main application using the venv's python
"$VENV_DIR/bin/python3" main.py
