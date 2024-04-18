#!/usr/bin/env python3
import os
import sys
import click
import re
from urllib.parse import unquote
from json import dumps


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

    if json:
        output = {
            "uri": recents[0],
            "sec": times[0],
            "path": path,
        }
        click.echo(dumps(output, indent=2))
    else:
        click.echo(path)


if __name__ == "__main__":
    recent_played_vlc()
