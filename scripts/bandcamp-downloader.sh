#!/bin/sh
DLS="$@"

if [ -z "$*" ]; then
   DLS=$(xsel -ob)
   echo "No args, using clipboard: $DLS";
fi

yt-dlp -f bestaudio[ext=mp3] --embed-thumbnail -o  "%(artist)s - %(playlist_title)s/%(playlist_index)s_%(track)s.%(ext)s" "$DLS"
echo "$DLS" >> $HOME/Music/bandcamps.txt
