#!/home/kevin/.virtualenvs/++scripts+music-history/bin/python3
import os
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
search_results = ytmusic.search(search_query, filter="songs")


def display_func(s):
    title = s.get("title", "?")
    try:
        artist = s.get("artists", ["?"])[0].get("name", "?")
    except (IndexError, KeyError) as e:
        artist = "?"
    album = s.get("album", {}).get("name", "?")
    return f"{title} - {artist} - {album}"


song = fzf_choose(search_results, display_func)


video_id = song["videoId"]
print(json.dumps(song, indent=2))
url = f"https://music.youtube.com/watch?v={video_id}"
print(url)
play_youtube_music_url(url=url)
largest_thumbnail = song["thumbnails"][-1]["url"]
subprocess.run(["timg", largest_thumbnail])
