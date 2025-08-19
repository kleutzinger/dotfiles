#!/usr/bin/env -S uv run --script --with click

"""
https://github.com/porjo/youtubeuploader

usage: vodbackup.py <URL>
where URL is the URL of the video to download, usually a twitch VOD.
"""

import subprocess
import os
import click
import shutil
import signal
import sys


CLIENT_SECRETS_PATH = os.path.join(
    os.path.expanduser("~"), ".config/youtubeuploader/client_secrets.json"
)
CLIENT_TOKEN_PATH = os.path.join(
    os.path.expanduser("~"), ".config/youtubeuploader/request.token"
)

assert os.path.exists(CLIENT_SECRETS_PATH), f"File not found: {CLIENT_SECRETS_PATH}"
assert os.path.exists(CLIENT_TOKEN_PATH), f"File not found: {CLIENT_TOKEN_PATH}"


@click.command()
@click.argument("url_or_path")
@click.option(
    "--cleanup", "-c", is_flag=True, help="Delete the downloaded file after uploading"
)
# add an option to specify bracket-url
@click.option(
    "-b",
    "--bracket-url",
    help="Bracket URL to use for the upload, if not specified, will use the default bracket URL",
)
# add a --title
@click.option(
    "-t",
    "--title",
    help="Specify the title of the video"

)
def main(url_or_path: str, cleanup: bool = False, bracket_url: str = "", title: str = ""):
    # Copy secrets to current dir
    secrets = [
        (CLIENT_SECRETS_PATH, os.path.basename(CLIENT_SECRETS_PATH)),
        (CLIENT_TOKEN_PATH, os.path.basename(CLIENT_TOKEN_PATH)),
    ]

    def cleanup_secrets(*_):
        for _, dest in secrets:
            try:
                if os.path.exists(dest):
                    os.remove(dest)
            except Exception as e:
                print(f"Warning: could not delete {dest}: {e}")

    # Register cleanup for signals
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: (cleanup_secrets(), sys.exit(1)))
    for src, dest in secrets:
        shutil.copy(src, dest)
    try:
        # check if url is a local absolute path that exists
        if os.path.exists(url_or_path):
            local_file = os.path.basename(url_or_path)
            video_files = [local_file]
        else:
            # Use yt-dlp to download and print the output filename
            result = subprocess.run(
                [
                    "uvx",
                    "--no-cache",
                    "yt-dlp",
                    "--print",
                    "after_move:filepath",
                    url_or_path,
                ],
                capture_output=True,
                text=True,
            )
            downloaded_file = (
                result.stdout.strip().splitlines()[-1]
                if result.stdout.strip()
                else None
            )
            if not downloaded_file or not os.path.exists(downloaded_file):
                print("Error: No file was downloaded.")
                return
            video_files = [downloaded_file]
        for file in video_files:
            print("Uploading", file)
            description_text = "Find all my vods at https://vods.kevbot.xyz"
            if bracket_url:
                description_text += f"\nBracket URL: {bracket_url}"
            if not title:
                title = os.path.basename(file)
            alphanumeric_title = "".join(
                [
                    c
                    for c in title
                    if c.isalnum() or c in [" ", "-", "_", "."]
                ]
            )
            # todo: install inline somehow
            subprocess.run(
                [
                    "youtubeuploader",
                    "-filename",
                    file,
                    "-privacy",
                    "unlisted",
                    "-description",
                    description_text,
                    "-title",
                    alphanumeric_title,
                ]
            )
        if cleanup:
            for file in video_files:
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Warning: could not delete {file}: {e}")
            print(f"Deleted all video files in current directory")
    finally:
        cleanup_secrets()


if __name__ == "__main__":
    main()
