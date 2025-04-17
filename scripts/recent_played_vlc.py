#!/usr/bin/env python3
import os
import plistlib
import re
import subprocess
import pathlib
import sys
from json import dumps
from urllib.parse import unquote

LINUX_CONFIG_PATH = os.path.expanduser("~/.config/vlc/vlc-qt-interface.conf")
MAC_CONFIG_PATH = os.path.expanduser("~/Library/Preferences/org.videolan.vlc.plist")
WINDOWS_CONFIG_PATH = os.path.expanduser(r"~\AppData\Roaming\vlc\vlc-qt-interface.ini")


def recent_and_time_linux_or_win(config_file_path:str) -> tuple[str, int]:
    if not os.path.exists(config_file_path):
        print(f"VLC configuration file not found at {config_file_path}")
        sys.exit(1)

    recent_line, times_line = "", ""
    with open(config_file_path, "r") as file:
        vlc_config = file.readlines()
    for line in vlc_config:
        if line.startswith("list="):
            recent_line = line
        if line.startswith("times"):
            times_line = line
    if not recent_line or not times_line:
        print("No recent played files found.")
        sys.exit(1)

    recents = recent_line.split("list=")[1].split(", ")
    # convert ms to seconds
    times = list(
        map(lambda t: int(t) // 1000, times_line.split("times=")[1].split(", "))
    )
    return recents[0], times[0]


def recent_and_time_mac() -> tuple[str, int]:
    # Filepath to the .plist file
    plist_path = MAC_CONFIG_PATH

    # Open and parse the .plist file
    with open(plist_path, "rb") as plist_file:
        plist_data = plistlib.load(plist_file)

    # Extract the recently played media list
    """
     'recentlyPlayedMedia': {'file:///Users/kevin/Downloads/BigBuckBunny_320x180 copy.mp4': 242,
                             'file:///Users/kevin/Downloads/BigBuckBunny_320x180.mp4': 184},
     'recentlyPlayedMediaList': ['file:///Users/kevin/Downloads/BigBuckBunny_320x180.mp4',
                                 'file:///Users/kevin/Downloads/BigBuckBunny_320x180 '
                                 'copy.mp4']
    """
    recently_played = plist_data.get("recentlyPlayedMediaList", [])[-1]
    # Extract the last played time
    last_played_time = plist_data.get("recentlyPlayedMedia", {}).get(recently_played, 0)
    return recently_played, last_played_time


def get_recent_played_vlc() -> tuple[str, int]:
    if sys.platform == "darwin":
        return recent_and_time_mac()
    elif sys.platform.startswith("linux"):
        return recent_and_time_linux_or_win(LINUX_CONFIG_PATH)
    elif sys.platform.startswith("win"):
        return recent_and_time_linux_or_win(WINDOWS_CONFIG_PATH)
    else:
        print(f"Unsupported operating system. {sys.platform} detected")
        sys.exit(1)


def recent_played_vlc():
    json = "--json" in sys.argv
    recent, time = get_recent_played_vlc()
    if sys.platform.startswith("win"):
        # example: file:///C:/Users/kevin/Videos/2025-04-13%2016-23-15.mp4
        raw_path = re.sub(r"^file:///", "", unquote(recent))
    else:
        raw_path = re.sub(r"^file://", "", unquote(recent))
        # replace any instances of '/./' with '/'
        raw_path = re.sub(r"/\./", "/", raw_path)
    path = pathlib.Path(raw_path)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    duration_cmd = [
        "ffprobe",
        "-i",
        path,
        "-show_entries",
        "format=duration",
        "-v",
        "quiet",
        "-of",
        "csv=p=0",
    ]
    try:
        duration = float(subprocess.check_output(duration_cmd).decode("utf-8").strip())
    except Exception as e:
        print(e, file=sys.stderr)
        duration = -1
    file_size = os.path.getsize(path)

    if json:
        output = {
            "uri": recent,
            "sec": time,
            "path": raw_path,
            "size": file_size,
            "duration": duration,
        }
        print(dumps(output, indent=2))
    else:
        print(raw_path)


if __name__ == "__main__":
    recent_played_vlc()
