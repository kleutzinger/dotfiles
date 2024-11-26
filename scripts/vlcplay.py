#!/usr/bin/env python3
"""
this is basically a port of the following fish statement
vlc (fd -a -e mkv -e webm -e mp4 -e m4v -e webm -e gif -e m4a -e wmv --follow | sort) --quiet
"""

import os
import subprocess
import urllib.parse

import click

VID_EXTENSIONS = {".mkv", ".webm", ".mp4", ".m4v", ".webm", ".gif", ".m4a", ".wmv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}
PLAYLIST_FILE = os.path.join("/tmp", "vids.m3u8")


@click.command(help="Play all videos in the current directory recursively in VLC")
@click.option("--videos", is_flag=True, help="Include videos in the playlist (default)")
@click.option("--images", is_flag=True, help="Include images in the playlist")
@click.option("--all", is_flag=True, help="Include all filetypes in the playlist")
@click.option("--latest", is_flag=True, help="Sort by latest modified date")
@click.option("--largest", is_flag=True, help="Sort by largest first")
@click.option("--query", help="Search for files with a given query")
def main(videos: bool, images: bool, all: bool, latest: bool, largest: bool, query: str) -> None:
    valid_extensions = set()
    if images:
        click.echo("adding images")
        valid_extensions.update(IMAGE_EXTENSIONS)
    if videos:
        click.echo("adding videos")
        valid_extensions.update(VID_EXTENSIONS)
    if all:
        click.echo("adding all")
        valid_extensions.update(VID_EXTENSIONS)
        valid_extensions.update(IMAGE_EXTENSIONS)
    if not valid_extensions:
        click.echo("defaulting to videos")
        valid_extensions.update(VID_EXTENSIONS)
    if os.path.exists(PLAYLIST_FILE):
        os.remove(PLAYLIST_FILE)
    vids = []
    for root, _dirs, files in os.walk("."):
        for file in files:
            if os.path.splitext(file)[-1].lower() in valid_extensions:
                abspath = os.path.abspath(os.path.join(root, file))
                vids.append(abspath)
    if query:
        vids = [vid for vid in vids if query.lower() in vid.lower()]
    if largest:
        vids = sorted(vids, key=os.path.getsize, reverse=True)
    elif latest:
        vids = sorted(vids, key=os.path.getmtime, reverse=True)
    else:
        vids = sorted(vids, key=lambda x: x.lower())
    # urlencode all vids
    vids = [urllib.parse.quote(vid) for vid in vids]

    with open(PLAYLIST_FILE, "w") as f:
        f.write("\n".join(vids))
    click.echo(f"Playing {len(vids)} videos in VLC")
    subprocess.run(["vlc", "--quiet", "--playlist-autostart", PLAYLIST_FILE])


if __name__ == "__main__":
    main()
