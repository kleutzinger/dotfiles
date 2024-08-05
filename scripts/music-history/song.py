#!/home/kevin/.virtualenvs/++scripts+music-history/bin/python3
import os
import sys
import shutil
import time
import subprocess

from importmonkey import add_path
from ytmusicapi import YTMusic

from lib import play_youtube_music_url
import json

compath = os.path.expanduser("~/scripts/")
add_path(compath)
from common import fzf_choose

ytmusic = YTMusic()
search_query = input("Enter the song name: ")
search_results_music = ytmusic.search(search_query, filter="songs")
search_results_video = ytmusic.search(search_query, filter="videos")


def display_func(s):
    title = s.get("title", "?")
    try:
        artist = s.get("artists", ["?"])[0].get("name", "?")
    except:
        artist = "?"
    try:
        album = s.get("album", {}).get("name", "?")
    except:
        album = "?"
    return f"{title} - {artist} - {album}"


separator = dict(title="-" * 20)

song = fzf_choose(
    search_results_music + [separator] + search_results_video, display_func
)


video_id = song["videoId"]
url = f"https://music.youtube.com/watch?v={video_id}"
print(url)
if "--url" in sys.argv:
    # put in clipboard via xsel
    if shutil.which("xsel"):
        subprocess.run(["xsel", "-b"], input=url.encode())
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "URL copied to clipboard " + url])
    exit(0)
print(json.dumps(song, indent=2))
play_youtube_music_url(url=url)
largest_thumbnail = song["thumbnails"][-1]["url"]
subprocess.run(["timg", largest_thumbnail])
time.sleep(3)
