#!/usr/bin/env python3

"""
https://github.com/porjo/youtubeuploader

usage: vodbackup.py <URL>
where URL is the URL of the video to download, usually a twitch VOD.
"""

import subprocess
import tempfile
import os
import click
import shutil


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
    "--cleanup", is_flag=True, help="Delete the downloaded file after uploading"
)
# add an option to specify bracket-url
@click.option(
    "--bracket-url",
    help="Bracket URL to use for the upload, if not specified, will use the default bracket URL",
)
def main(url_or_path: str, cleanup: bool = False, bracket_url: str = ""):
    alnum_url = "".join([c for c in url_or_path if c.isalnum()])
    tmpdirpath = f"vodbackup-{alnum_url}"
    os.mkdir(tmpdirpath)
    tmpdirpath = os.path.abspath(tmpdirpath)
    print("Created temporary directory", tmpdirpath)
    # check if url is is a local absolute path that exists
    if os.path.exists(url_or_path):
        shutil.copy(url_or_path, tmpdirpath)
        print(f"Copied local file {url_or_path} to {tmpdirpath}")
        os.chdir(tmpdirpath)
    else:
        os.chdir(tmpdirpath)
        subprocess.run(["yt-dlp", url_or_path])
    # copy secrets to current dir
    shutil.copy(CLIENT_SECRETS_PATH, tmpdirpath)
    shutil.copy(CLIENT_TOKEN_PATH, tmpdirpath)
    for file in os.listdir(tmpdirpath):
        if file.endswith(".mp4"):
            print("Uploading", file)
            description_text = "Find all my vods at https://vods.kevbot.xyz"
            if bracket_url:
                description_text += f"\nBracket URL: {bracket_url}"
            subprocess.run(
                [
                    "youtubeuploader",
                    "-filename",
                    file,
                    "-privacy",
                    "unlisted",
                    "-description",
                    description_text,
                ]
            )
    if cleanup:
        # delete all files in tempdir
        for file in os.listdir(tmpdirpath):
            os.remove(file)
        print(f"Deleted all files in {tmpdirpath}")


if __name__ == "__main__":
    main()
