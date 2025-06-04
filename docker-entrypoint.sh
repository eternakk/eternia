#!/bin/bash
set -e

# Function to start the API server
start_api() {
    echo "Starting Eternia API server..."
    exec python -m uvicorn services.api.server:app --host 0.0.0.0 --port 8000 --reload
}

# Function to start the simulation
start_simulation() {
    echo "Starting Eternia simulation..."
    exec python main.py "$@"
}

# Main entrypoint logic
case "$1" in
    api)
        shift
        start_api "$@"
        ;;
    simulation)
        shift
        start_simulation "$@"
        ;;
    *)
        echo "Usage: $0 {api|simulation} [args...]"
        echo "  api         - Start the API server"
        echo "  simulation  - Start the simulation (can pass additional args like --cycles 20)"
        exit 1
        ;;
esac