#!/usr/bin/env python3
"""
this is basically a port of the following fish statement
vlc (fd -a -e mkv -e webm -e mp4 -e m4v -e webm -e gif -e m4a -e wmv --follow | sort) --quiet
"""

import os
import subprocess

import click

VID_EXTENSIONS = {".mkv", ".webm", ".mp4", ".m4v", ".webm", ".gif", ".m4a", ".wmv"}
PLAYLIST_FILE = "/tmp/vids.m3u"


@click.command(help="Play all videos in the current directory recursively in VLC")
def main():
    if os.path.exists(PLAYLIST_FILE):
        os.remove(PLAYLIST_FILE)
    vids = []
    for root, _dirs, files in os.walk("."):
        for file in files:
            if os.path.splitext(file)[-1].lower() in VID_EXTENSIONS:
                abspath = os.path.abspath(os.path.join(root, file))
                vids.append(abspath)
    vids = sorted(vids, key=lambda x: x.lower())
    with open(PLAYLIST_FILE, "w") as f:
        f.write("\n".join(vids))
    click.echo(f"Playing {len(vids)} videos in VLC")
    subprocess.run(["vlc", "--quiet", "--playlist-autostart", PLAYLIST_FILE])


if __name__ == "__main__":
    main()
