#!/bin/bash

# Outputs the middle frame of a video file as a PNG image.

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 input_video [output_frame]"
    exit 1
fi

input_video="$1"
output_frame="${2:-output.png}"

ffmpeg -y -i "$input_video" -ss $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$input_video" | awk '{print ($1/2)}') -vframes 1 "$output_frame"
