#!/bin/sh
set -x
DLS="$@"

if [ -z "$*" ]; then
   DLS=$(xsel -ob)
   echo "No args, using clipboard: $DLS";
fi

# put download here to start
TMP=$(mktemp --directory)
pushd $TMP
yt-dlp -f bestaudio[ext=mp3] --embed-thumbnail -o  "%(artist)s - %(playlist_title)s/%(playlist_index)s_%(track)s.%(ext)s" "$DLS"
# folder with most subdirs / files contained therein
# aka the most common artist of the album
LARGEST_FOLDER="$(find . -type d | cut -d/ -f 2 | uniq -c | sort -g | tail -n 1 | awk '{$1=""}1' | awk '{$1=$1}1')"
popd
mkdir "$LARGEST_FOLDER"
fd . --extension mp3 $TMP/ | xargs -I files cp files "$LARGEST_FOLDER"
echo "$DLS" >> $HOME/Music/bandcamps.txt
