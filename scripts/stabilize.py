#!/usr/bin/env python3
# use ffmpeg to stabilize a given video path to an ouptut file

import os
import subprocess
import sys


def stabilize_video(video_path, output_path):
    # check if the video path exists
    if not os.path.exists(video_path):
        print("The video path does not exist")
        return

    # check if the output path exists
    if os.path.exists(output_path):
        print("The output path already exists")
        return

    # run ffmpeg command to stabilize the video
    import subprocess

    # First command
    command = ["ffmpeg", "-i", video_path, "-vf", "vidstabdetect", "-f", "null", "-"]
    subprocess.run(command)

    # Second command
    command = ["ffmpeg", "-i", video_path, "-vf", "vidstabtransform", output_path]
    subprocess.run(command)

    os.remove("transforms.trf")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stabilize.py <video_path> <output_path>(optional)")
        sys.exit(1)

    video_path = sys.argv[1]
    # check no output path provided
    if len(sys.argv) == 2:
        name, extension = os.path.splitext(video_path)
        output_path = f"{name}-stable{extension}"
    else:
        output_path = sys.argv[2]

    stabilize_video(video_path, output_path)
