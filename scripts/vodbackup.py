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
@click.argument("url")
def main(url):
    with tempfile.TemporaryDirectory(delete=False) as tmpdirname:
        print("Created temporary directory", tmpdirname)
        os.chdir(tmpdirname)
        subprocess.run(["yt-dlp", url])
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
                    ]
                )


if __name__ == "__main__":
    main()
