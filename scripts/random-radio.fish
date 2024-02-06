#!/bin/fish

cd ~/gits
# check if directory  m3u-radio-music-playlists exists
if test -d m3u-radio-music-playlists
    echo "m3u-radio-music-playlists exists"
    cd m3u-radio-music-playlists
    git pull
else
    echo "m3u-radio-music-playlists does not exist"
    git clone --depth 1 https://github.com/junguler/m3u-radio-music-playlists
end

# pick a random m3u file and play it
set station (random choice (fd --extension m3u))
echo "Playing $station"
vlc -Z $station
