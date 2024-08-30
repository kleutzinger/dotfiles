#!/usr/bin/env bash

# Define the directory path and GitHub repository URL
TRILIUM_DIR=~/gits/trilium
REPO_URL=https://github.com/zadam/trilium.git

# Check if the directory exists
if [ ! -d "$TRILIUM_DIR" ]; then
    echo "Directory $TRILIUM_DIR does not exist. Cloning from GitHub..."
    git clone $REPO_URL $TRILIUM_DIR
fi

# Change to the docs directory
pushd $TRILIUM_DIR/docs

# Start the server in the background and store its PID
python -m http.server 8022 &
SERVER_PID=$!

# Function to kill the server process
cleanup() {
    echo "Stopping server..."
    kill $SERVER_PID
    wait $SERVER_PID
    popd
    exit 0
}

# Trap SIGINT (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# Open the browser
python -m webbrowser -t "http://localhost:8022"

# Wait for the server process to complete
wait $SERVER_PID
