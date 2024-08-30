#!/usr/bin/env bash

# Get the directory where the script is located
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Loop over each directory in the script's location directory
for dir in "$SCRIPT_DIR"/*/; do
    # Remove trailing slash for better directory handling
    dir=${dir%/}

    # Skip if it's not a directory
    if [ ! -d "$dir" ]; then
	continue
    fi

    # Change to the directory
    cd "$dir" || { echo "Failed to cd into $dir"; continue; }

    # Run docker compose command
    echo "Starting project: $(basename "$dir")"
    docker compose --env-file ../secret.env up -d --force-recreate

    # Return to the script's location directory
    cd "$SCRIPT_DIR" || { echo "Failed to return to $SCRIPT_DIR"; exit 1; }
done
