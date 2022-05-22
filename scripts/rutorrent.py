#!/usr/bin/env python3
"""
# rutorrent.py

This scripts takes a magnet link and initiates a download on your rutorrent
instance via a post request.

## Usage

you have three ways to provide a magnet link to this script, in order of
precedence

    1. cli argument
        python rutorrent.py '<magnet_link>'
    2. clipboard (pip install pyperclip)
        *copy magnet link to clipboard*
        python rutorrent.py
    3. interactive prompt
        python rutorrent.py
        *input magnet link*


## Download Directory Selection

Additionally, supplying s in any of the above calls lets you select a directory
you want the torrent to go. Without this arg it defaults to the movies dir.

example:
    python rutorrent.py s <magnet_link>
    * interactively select desired download location *
"""

import sys
import os
import requests
import dotenv

try:
    import pyperclip

    clipboard_support = True
except ImportError:
    clipboard_support = False


dotenv.load_dotenv(override=True)

# https://my-example-rutorrent-server.net
RUTORRENT_URL = os.environ.get("RUTORRENT_URL")

DEFAULT_TORRENT_LABEL = "kevin"
DEFAULT_DOWNLOAD_DIR = "/mnt/shared/media/movies"


def dir_prompt() -> str:
    """
    interacitvely choose a single entry from paths.
    use this by suppying `s` as an additional command line parameter
    """
    paths = [
        "/mnt/shared/media/movies",
        "/mnt/shared/media/tvshows",
        "/mnt/shared/media/torrents",
    ]
    valid_answers = [str(i) for i in range(len(paths))]
    while True:
        print("\n".join([f"{i}: {d}" for i, d in enumerate(paths)]))
        given_ans = input(f"input: {list(range(len(paths)))}: ")
        if given_ans in valid_answers:
            return paths[int(given_ans)]


def download_magnet(
    magnet: str,
    directory: str = DEFAULT_DOWNLOAD_DIR,
    label: str = DEFAULT_TORRENT_LABEL,
) -> tuple[int, str]:
    """
    send a post request to download a magnet link
    returns the status_code and text of the response
    """
    print(f"downloading to {directory}")
    resp = requests.request(
        method="POST",
        url=f"{RUTORRENT_URL}/php/addtorrent.php?dir_edit={directory}&label={label}",
        data={"url": magnet},
        verify=True,
    )

    # this should say success somewhere in it
    return resp.status_code, resp.text


def is_magnet(text: str) -> bool:
    "approximately check if a link is a magnet link"
    return text.startswith("magnet:")


def main() -> None:
    # arg
    if any([is_magnet(a) for a in sys.argv]):
        for a in sys.argv:
            if is_magnet(a):
                magnet = a.strip()
                break
    # clipboard
    elif clipboard_support and is_magnet(pyperclip.paste()):
        print("magnet link found in clipboard")
        magnet = pyperclip.paste()
    # prompt
    else:
        while True:
            magnet = input("input magnet link: ").strip()
            if is_magnet(magnet):
                break
            else:
                print("bad input")
    dl_dir = DEFAULT_DOWNLOAD_DIR
    if "s" in sys.argv:
        dl_dir = dir_prompt()
    out = download_magnet(magnet, dl_dir)
    print(out)


if __name__ == "__main__":
    main()
