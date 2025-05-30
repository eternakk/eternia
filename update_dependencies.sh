#!/bin/bash

# Exit on error
set -e

# Update dependencies to fix pydantic compatibility issue with Python 3.12
echo "Updating dependencies..."

# First, uninstall the problematic packages to avoid conflicts
echo "Removing existing packages..."
pip uninstall -y fastapi pydantic starlette || true

# Then install the correct versions from requirements.txt
echo "Installing updated packages..."
pip install -r requirements.txt --no-cache-dir

# Verify the installed versions
echo "Verifying installed versions..."
FASTAPI_VERSION=$(pip list | grep fastapi | awk '{print $2}')
PYDANTIC_VERSION=$(pip list | grep "^pydantic " | awk '{print $2}')

echo "Installed FastAPI version: $FASTAPI_VERSION"
echo "Installed Pydantic version: $PYDANTIC_VERSION"

# Check if the versions match what's expected
if [[ "$FASTAPI_VERSION" != "0.103.1" ]]; then
    echo "Warning: FastAPI version is $FASTAPI_VERSION, expected 0.103.1"
    echo "You may need to recreate your virtual environment."
fi

if [[ "$PYDANTIC_VERSION" != "2.4.0" ]]; then
    echo "Warning: Pydantic version is $PYDANTIC_VERSION, expected 2.4.0"
    echo "You may need to recreate your virtual environment."
fi

echo "Dependencies updated successfully."
echo "Please restart your application to apply the changes."
