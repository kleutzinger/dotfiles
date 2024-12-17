#!/usr/bin/env bash

# Check if a file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <input_file.mkv>"
    exit 1
fi

input_file="$1"

# Extract and format chapters without decimals
mkvinfo "$input_file" | awk '
/\+ Chapter time start:/ {
    # Extract the start timestamp
    split($0, arr, ": ");
    timestamp = arr[2];
    # Remove decimals
    sub(/\..*$/, "", timestamp);
}
/\+ Chapter string:/ {
    # Extract the chapter title
    split($0, arr, ": ");
    title = arr[2];
    # Print the formatted output
    printf "%s %s\n", timestamp, title;
}' | tee chapters.txt

# Check if the chapters.txt file was successfully created
if [ -s chapters.txt ]; then
    echo "Chapters exported to chapters.txt"
else
    echo "No chapters found or chapters.txt is empty."
fi
