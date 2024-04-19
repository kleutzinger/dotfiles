#!/usr/bin/env python3
import os
import re
import shlex
import subprocess
import sys
from json import dumps
from urllib.parse import unquote

import click


@click.command()
@click.option(
    "--json",
    is_flag=True,
    default=False,
    help="Print the output in JSON format.",
)
def recent_played_vlc(json):
    config_file_path = os.path.expanduser("~/.config/vlc/vlc-qt-interface.conf")
    if not os.path.exists(config_file_path):
        click.echo("VLC configuration file not found.")
        sys.exit(1)

    recent_line, times_line = None, None
    with open(config_file_path, "r") as file:
        vlc_config = file.readlines()
    for line in vlc_config:
        if line.startswith("list="):
            recent_line = line
        if line.startswith("times"):
            times_line = line
    if not recent_line or not times_line:
        click.echo("No recent played files found.")
        sys.exit(1)

    recents = recent_line.split("list=")[1].split(", ")
    # convert ms to seconds
    times = list(
        map(lambda t: int(t) // 1000, times_line.split("times=")[1].split(", "))
    )
    path = re.sub(r"^file://", "", unquote(recents[0]))

    duration_cmd = ["ffprobe", "-i", path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
    try:
        duration = float(subprocess.check_output(duration_cmd).decode("utf-8").strip())
    except Exception as e:
        print(e, file=sys.stderr)
        duration = -1
    file_size = os.path.getsize(path)

    if json:
        output = {
            "uri": recents[0],
            "sec": times[0],
            "path": path,
            "size": file_size,
            "duration": duration,
        }
        click.echo(dumps(output, indent=2))
    else:
        click.echo(path)


if __name__ == "__main__":
    recent_played_vlc()
