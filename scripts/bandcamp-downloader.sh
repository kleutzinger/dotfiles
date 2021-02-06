#!/bin/sh
# if [ -z "$*" ]; then echo "No args"; exit 0 fi

youtube-dl -f bestaudio[ext=mp3] --embed-thumbnail -o  "%(artist)s - %(playlist_title)s/%(playlist_index)s_%(track)s.%(ext)s" "$@"
