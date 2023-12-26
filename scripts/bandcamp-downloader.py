#!/usr/bin/env python3
import os
import subprocess
import tempfile
import sys
import shutil
import shlex
from urllib.parse import urlsplit, urlunsplit


def remove_query_params_and_fragment(url):
    return urlunsplit(urlsplit(url)._replace(query="", fragment=""))


def main():
    DL_URL = sys.argv[1] if len(sys.argv) > 1 else None

    if not DL_URL:
        DL_URL = subprocess.check_output(["xsel", "-ob"]).decode().strip()
        print(f"No args, using clipboard: {DL_URL}")

    if "?" in DL_URL or "#" in DL_URL:
        DL_URL = remove_query_params_and_fragment(DL_URL)
        print(f"Removed query params: {DL_URL}")

    CWD = os.getcwd()

    full_cmd = [
        "yt-dlp",
        "-f",
        "bestaudio[ext=mp3]",
        "--embed-thumbnail",
        "-o",
        "%(artist)s - %(playlist_title)s/%(playlist_index)s %(track)s.%(ext)s",
        DL_URL,
    ]
    # shlex.join is used for quoting, and we replace single quotes with double quotes to pass to sqlite
    joined_cmd = shlex.join(full_cmd).replace("'", '"')
    if os.environ.get("USER") == "kevin":
        subprocess.run(["turso", "auth", "login"])
        subprocess.run(
            [
                "turso",
                "db",
                "shell",
                "bandcamps",
                f"insert into downloads (url, full_cmd, cwd) values('{DL_URL}', '{joined_cmd}', '{CWD}');",
            ]
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
