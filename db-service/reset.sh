#!/bin/bash

# Script to reset the Python virtual environment

# Define the virtual environment directory name
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

echo "--- Starting Python Environment Reset ---"

# 1. Deactivate virtual environment if currently active
# This is a bit tricky to do reliably from within a script that might itself be run
# from an active venv. 'deactivate' is a shell function.
# If you run this script using 'source ./reset.sh', it can deactivate.
# If you run it as './reset.sh', it runs in a subshell and 'deactivate' won't affect the parent shell.
# For simplicity, we'll assume you might manually deactivate or that the subshell behavior is acceptable.
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating current virtual environment (if applicable in this shell)..."
    # Note: deactivate might not work as expected if script is not sourced.
    # It's safer to run this script from a shell where the venv is not active,
    # or to manually deactivate before running.
    deactivate || echo "Deactivate command not found or failed (this is okay if not in an active venv)."
fi

# 2. Remove the existing virtual environment directory
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing virtual environment: $VENV_DIR"
    rm -rf "$VENV_DIR"
    if [ $? -eq 0 ]; then
        echo "Successfully removed $VENV_DIR."
    else
        echo "ERROR: Failed to remove $VENV_DIR. Please check permissions or remove manually."
        exit 1
    fi
else
    echo "No existing virtual environment '$VENV_DIR' found to remove."
fi

# 3. Create a new virtual environment
echo "Creating new virtual environment: $VENV_DIR"
python3 -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment. Make sure python3 and python3-venv are installed."
    exit 1
fi
echo "Virtual environment created."

# 4. Activate the new virtual environment (for the context of this script)
# To make the activation persist in your current shell after the script finishes,
# you would need to *source* this script: `source ./reset.sh`
echo "Activating the new virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    # Attempt to inform user about sourcing if activation failed in subshell
    echo "If activation failed, try running this script by sourcing it: 'source ./reset.sh'"
    exit 1
fi
echo "Virtual environment activated."
echo "Current Python: $(which python)"

# 5. Upgrade pip, setuptools, and wheel
echo "Upgrading pip, setuptools, and wheel..."
pip install -U pip setuptools wheel
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to upgrade pip/setuptools/wheel."
    exit 1
fi
echo "Core packaging tools upgraded."

# 6. Install dependencies from requirements.txt
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies from $REQUIREMENTS_FILE."
        exit 1
    fi
    echo "Dependencies installed successfully."
else
    echo "WARNING: $REQUIREMENTS_FILE not found. Skipping dependency installation."
fi

echo "--- Python Environment Reset Complete ---"
echo "Virtual environment '$VENV_DIR' is ready and activated (in this script's context)."
echo "If you did not source the script (e.g., 'source ./reset.sh'),"
echo "you may need to manually activate it in your terminal: source $VENV_DIR/bin/activate"
