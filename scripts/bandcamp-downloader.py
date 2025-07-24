#!/home/kevin/.virtualenvs/++scripts/bin/python
import asyncio
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pprint import pprint
from urllib.parse import urlsplit, urlunsplit

from common import tryInsertIntoPocketBase as insertIntoPocketBase

# python function to download a webpage by url and find the <title> tag conents without any libraries


def get_title(url):
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.title.string


def remove_query_params_and_fragment(url):
    return urlunsplit(urlsplit(url)._replace(query="", fragment=""))


def main() -> None:
    DL_URL = sys.argv[1] if len(sys.argv) > 1 else None

    if not DL_URL:
        DL_URL = subprocess.check_output(["xsel", "-ob"]).decode().strip()
        print(f"No args, using clipboard: {DL_URL}")

    if "bandcamp.com" in DL_URL and ("?" in DL_URL or "#" in DL_URL):
        DL_URL = remove_query_params_and_fragment(DL_URL)
        print(f"Removed query params: {DL_URL}")

    CWD = os.getcwd()

    full_cmd = [
        "yt-dlp",
        "-f",
        "bestaudio",
        "--embed-thumbnail",
        "-o",
        "%(artist)s - %(playlist_title)s/%(playlist_index)s %(track)s.%(ext)s",
        DL_URL,
    ]
    # shlex.join is used for quoting, and we replace single quotes with double quotes to pass to sqlite
    joined_cmd = shlex.join(full_cmd)
    hostname = os.uname().nodename
    page_title = get_title(DL_URL)
    insertIntoPocketBase(
        {
            "url": DL_URL,
            "title": page_title,
            "full_cmd": joined_cmd,
            "cwd": CWD,
            "hostname": hostname,
        },
        db_name="bandcamps",
    )

    # put download here to start
    tmp_dir = tempfile.mkdtemp(prefix="bandcamp-")
    start_dir = os.getcwd()
    os.chdir(tmp_dir)

    subprocess.run(full_cmd)

    # folder with largest size
    # aka the most common artist of the album which we set as the album artist
    largest_folder = max(os.listdir(), key=lambda x: os.path.getsize(x))
    os.chdir(start_dir)
    # capitalize first letter of largest_folder
    output_dir = os.path.join(start_dir, largest_folder[0].upper() + largest_folder[1:])
    os.mkdir(output_dir)

    for root, _, files in os.walk(tmp_dir):
        for file in files:
            if file.endswith(".mp3"):
                source_path = os.path.join(root, file)
                shutil.copy2(source_path, output_dir)

    with open(os.path.join(os.environ["HOME"], "Music", "bandcamps.txt"), "a") as f:
        f.write(f"{DL_URL}\n")


if __name__ == "__main__":
    main()
