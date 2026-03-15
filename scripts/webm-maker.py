#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "click",
# ]
# ///

import subprocess
import json
import os
import sys
import click

MAX_FILE_SIZE = 2900  # KB, slightly under limit


def get_video_duration(input_file: str) -> float:
    """Use ffprobe to get the video duration in seconds."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_entries",
            "format=duration",
            input_file,
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--resolution",
    "-r",
    default=None,
    type=int,
    help="Vertical resolution (e.g. 720). Horizontal scales proportionally.",
)
@click.option(
    "--rotate",
    "-R",
    default=None,
    type=click.Choice(["0", "1", "2", "3"]),
    help="Transpose: 0=CCW+VFlip, 1=CW, 2=CCW, 3=CW+VFlip",
)
@click.option("--no-audio", "-a", "remove_audio", is_flag=True, help="Remove audio.")
@click.option(
    "--start", "-s", default=None, type=float, help="Start offset in seconds."
)
@click.option("--duration", "-d", default=None, type=float, help="Duration in seconds.")
def main(input_file, resolution, rotate, remove_audio, start, duration):
    """Convert a video file to a WebM using two-pass VP8 encoding."""

    # Build -vf filter chain
    vf_filters = []
    if resolution is not None:
        vf_filters.append(f"scale=-1:{resolution}")
    if rotate is not None:
        vf_filters.append(f"transpose={rotate}")

    # Determine duration for bitrate calculation
    if duration is None:
        click.echo("No duration specified, probing source video length...")
        duration = get_video_duration(input_file)
        click.echo(f"Using source video length: {duration:.2f} seconds")

    bitrate = int(8 * MAX_FILE_SIZE / duration)
    click.echo(f"Target bitrate: {bitrate}K")

    # Build shared ffmpeg args
    base_args = [
        "-i",
        input_file,
        "-c:v",
        "libvpx",
        f"-b:v",
        f"{bitrate}K",
        "-quality",
        "best",
    ]

    if vf_filters:
        base_args += ["-vf", ",".join(vf_filters)]
    if start is not None:
        base_args += ["-ss", str(start)]
    if duration is not None:
        base_args += ["-t", str(duration)]
    if remove_audio:
        base_args += ["-an"]
        click.echo("Removing audio")
    else:
        click.echo("Keeping audio")

    base_args += ["-sn", "-threads", "0"]

    output_file = os.path.splitext(input_file)[0] + ".webm"

    # Pass 1
    click.echo("\nRunning pass 1...")
    subprocess.run(
        ["ffmpeg"] + base_args + ["-f", "webm", "-pass", "1", "-y", os.devnull],
        check=True,
    )

    # Pass 2
    click.echo("Running pass 2...")
    subprocess.run(
        ["ffmpeg"] + base_args + ["-pass", "2", "-y", output_file],
        check=True,
    )

    # Cleanup
    for log in ["ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"]:
        if os.path.exists(log):
            os.remove(log)

    click.echo(f"\nFinished! Output: {output_file}")


if __name__ == "__main__":
    main()
