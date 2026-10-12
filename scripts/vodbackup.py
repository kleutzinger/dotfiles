#!/usr/bin/env -S uv run --script --with click

"""
https://github.com/porjo/youtubeuploader

usage: vodbackup.py <URL>
where URL is the URL of the video to download, usually a twitch VOD.
"""

import subprocess
import os
import click
import sys
from datetime import datetime


CLIENT_SECRETS_PATH = os.path.join(
    os.path.expanduser("~"), ".config/youtubeuploader/client_secrets.json"
)
CLIENT_TOKEN_PATH = os.path.join(
    os.path.expanduser("~"), ".config/youtubeuploader/request.token"
)

assert os.path.exists(CLIENT_SECRETS_PATH), f"File not found: {CLIENT_SECRETS_PATH}"
assert os.path.exists(CLIENT_TOKEN_PATH), f"File not found: {CLIENT_TOKEN_PATH}"


@click.command()
@click.argument("url_or_path", required=False)
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
    help="Specify the title of the video",
)
@click.option(
    "-d",
    "--description",
    help="Additional text to append to the description",
)
@click.option(
    "-l",
    "--local-video-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a local video file to upload, instead of URL_OR_PATH",
)
@click.option(
    "-s",
    "--stream",
    is_flag=True,
    help="Pipe yt-dlp straight into youtubeuploader without saving to disk",
)
@click.option(
    "--background",
    is_flag=True,
    help="Detach and keep running after the terminal closes, logging to ~/.local/state/vodbackup/",
)
def main(
    url_or_path: str = None,
    cleanup: bool = False,
    bracket_url: str = "",
    title: str = "",
    description: str = "",
    local_video_file: str = None,
    stream: bool = False,
    background: bool = False,
):
    if not url_or_path and not local_video_file:
        raise click.UsageError("Provide either URL_OR_PATH or --local-video-file")
    if url_or_path and local_video_file:
        raise click.UsageError("Provide only one of URL_OR_PATH or --local-video-file")
    if stream and (local_video_file or os.path.exists(url_or_path)):
        raise click.UsageError("--stream only works with a URL")
    if background:
        # Re-run this script detached in its own session so it survives SSH hangups
        log_dir = os.path.expanduser("~/.local/state/vodbackup")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(
            log_dir, f"{datetime.now():%Y%m%d-%H%M%S}-{os.getpid()}.log"
        )
        args = [a for a in sys.argv[1:] if a != "--background"]
        with open(log_path, "w") as log:
            proc = subprocess.Popen(
                [sys.executable, os.path.abspath(__file__), *args],
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
        print(f"Running in background (pid {proc.pid}). Follow output with:")
        print(f"  tail -f {log_path}")
        return
    download_proc = None
    # check if url is a local absolute path that exists
    if local_video_file:
        video_files = [local_video_file]
    elif os.path.exists(url_or_path):
        local_file = os.path.basename(url_or_path)
        video_files = [local_file]
    elif stream:
        if not title:
            title = subprocess.run(
                ["uvx", "--no-cache", "yt-dlp", "--print", "title", url_or_path],
                capture_output=True,
                text=True,
            ).stdout.strip()
        # Video goes yt-dlp stdout -> youtubeuploader stdin, never touching disk
        download_proc = subprocess.Popen(
            ["uvx", "--no-cache", "yt-dlp", "-o", "-", url_or_path],
            stdout=subprocess.PIPE,
        )
        video_files = ["-"]
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
        print("Uploading to youtube", file)
        description_text = "Find all my vods at https://vods.kevbot.xyz"
        if bracket_url:
            description_text += f"\nBracket URL: {bracket_url}"
        if description:
            description_text += description
        if not title:
            title = os.path.basename(file)
        sanitized_title = "".join(
            [
                c
                for c in title
                if c.isalnum() or c in [" ", "-", "_", ".", "$", "@", "[", "]"]
            ]
        )
        # todo: install inline somehow
        subprocess.run(
            [
                "youtubeuploader",
                "-secrets",
                CLIENT_SECRETS_PATH,
                "-cache",
                CLIENT_TOKEN_PATH,
                "-filename",
                file,
                "-privacy",
                "unlisted",
                "-description",
                description_text,
                "-title",
                sanitized_title,
            ],
            stdin=download_proc.stdout if download_proc else None,
        )
    if download_proc:
        download_proc.stdout.close()
        if download_proc.wait() != 0:
            print("Warning: yt-dlp exited with an error, the upload may be incomplete")
        return
    if cleanup:
        for file in video_files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Warning: could not delete {file}: {e}")
        print(f"Deleted all video files in current directory")


if __name__ == "__main__":
    main()
