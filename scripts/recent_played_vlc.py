#!/usr/bin/env python3
import os
import plistlib
import re
import subprocess
import sys
from json import dumps
from urllib.parse import unquote

LINUX_CONFIG_PATH = os.path.expanduser("~/.config/vlc/vlc-qt-interface.conf")
MAC_CONFIG_PATH = os.path.expanduser("~/Library/Preferences/org.videolan.vlc.plist")


def recent_and_time_linux() -> tuple[str, int]:
    config_file_path = os.path.expanduser(LINUX_CONFIG_PATH)
    if not os.path.exists(config_file_path):
        print("VLC configuration file not found.")
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
        return recent_and_time_linux()
    else:
        print("Unsupported operating system.")
        sys.exit(1)


def recent_played_vlc():
    json = "--json" in sys.argv
    recent, time = get_recent_played_vlc()
    path = re.sub(r"^file://", "", unquote(recent))
    # replace any instances of '/./' with '/'
    path = re.sub(r"/\./", "/", path)

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
            "path": path,
            "size": file_size,
            "duration": duration,
        }
        print(dumps(output, indent=2))
    else:
        print(path)


if __name__ == "__main__":
    recent_played_vlc()
