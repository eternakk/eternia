#!/bin/bash

# Script to clean up misplaced data directories in the docs directory

echo "Cleaning up misplaced data directories in docs..."

# Remove artifacts directory in docs
if [ -d "docs/artifacts" ]; then
    echo "Removing docs/artifacts directory..."
    rm -rf docs/artifacts
fi

# Remove config directory in docs
if [ -d "docs/config" ]; then
    echo "Removing docs/config directory..."
    rm -rf docs/config
fi

# Remove data directory in docs
if [ -d "docs/data" ]; then
    echo "Removing docs/data directory..."
    rm -rf docs/data
fi

# Remove logs directory in docs
if [ -d "docs/logs" ]; then
    echo "Removing docs/logs directory..."
    rm -rf docs/logs
fi

echo "Cleanup complete!"
echo "Data files should only be stored in their appropriate directories at the root level:"
echo "- artifacts/ for artifact files"
echo "- config/ for configuration files"
echo "- data/ for database and other data files"
echo "- logs/ for log files"