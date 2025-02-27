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
def main(url_or_path: str, cleanup: bool = False):
    alnum_url = "".join([c for c in url_or_path if c.isalnum()])
    tmpdirname = tempfile.mkdtemp(prefix=f"vodbackup-{alnum_url}-")
    print("Created temporary directory", tmpdirname)
    # check if url is is a local absolute path that exists
    if os.path.exists(url_or_path):
        shutil.copy(url_or_path, tmpdirname)
        print(f"Copied local file {url_or_path} to {tmpdirname}")
        os.chdir(tmpdirname)
    else:
        os.chdir(tmpdirname)
        subprocess.run(["yt-dlp", url_or_path])
    # copy secrets to current dir
    shutil.copy(CLIENT_SECRETS_PATH, tmpdirname)
    shutil.copy(CLIENT_TOKEN_PATH, tmpdirname)
    for file in os.listdir(tmpdirname):
        if file.endswith(".mp4"):
            print("Uploading", file)
            subprocess.run(
                [
                    "youtubeuploader",
                    "-filename",
                    file,
                    "-privacy",
                    "unlisted",
                    "-description",
                    "Find all my vods at https://vods.kevbot.xyz",
                ]
            )
    if cleanup:
        # delete all files in tempdir
        for file in os.listdir(tmpdirname):
            os.remove(file)
        print(f"Deleted all files in {tmpdirname}")


if __name__ == "__main__":
    main()
