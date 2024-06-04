#!/home/kevin/.virtualenvs/++scripts+music-history/bin/python3
import os
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
    album = s.get("album", {}).get("name", "?")
    return f"{title} - {artist} - {album}"

separator = dict(title="-"*20)

song = fzf_choose(search_results_music + [separator] + search_results_video, display_func)


video_id = song["videoId"]
print(json.dumps(song, indent=2))
url = f"https://music.youtube.com/watch?v={video_id}"
print(url)
play_youtube_music_url(url=url)
largest_thumbnail = song["thumbnails"][-1]["url"]
subprocess.run(["timg", largest_thumbnail])
time.sleep(3)
