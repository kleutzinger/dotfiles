#!/bin/sh
set -x
DLS="$@"

if [ -z "$*" ]; then
   DLS=$(xsel -ob)
   echo "No args, using clipboard: $DLS";
fi

# if user is named kevin, do the following
if [ "$USER" = "kevin" ]; then
  set -e
  turso db shell bandcamps "insert into downloads (url) values('$DLS');"
  set +e
fi

# put download here to start
TMP=$(mktemp --directory)
pushd $TMP
yt-dlp -f bestaudio[ext=mp3] --embed-thumbnail -o  "%(artist)s - %(playlist_title)s/%(playlist_index)s %(track)s.%(ext)s" "$DLS"
# folder with largest size
# aka the most common artist of the album which we set as the album artist
LARGEST_FOLDER="$(du --max-depth=1 . | sort -r -k1,1n | tail -2 | head -1 | cut -f2 | sed 's/^.\///')"
popd
mkdir "$LARGEST_FOLDER"
find $TMP/ -name '*.mp3' -print0 | xargs -0 -I files cp files "$LARGEST_FOLDER"
echo "$DLS" >> $HOME/Music/bandcamps.txt

