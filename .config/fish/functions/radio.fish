function radio --description 'play a random radio station from m3u-radio-music-playlists'
    cd ~/gits
    # check if directory  m3u-radio-music-playlists exists
    if test -d m3u-radio-music-playlists
        echo "m3u-radio-music-playlists exists"
        cd m3u-radio-music-playlists
    else
        echo "m3u-radio-music-playlists does not exist"
        git clone --depth 1 https://github.com/junguler/m3u-radio-music-playlists
        cd m3u-radio-music-playlists
    end

    # pick a random m3u file and play it
    set station (fd --extension m3u | sort -R | rofi -dmenu -p "Select station")

    if test -z $station
        echo "No station selected"
        exit 1
    end

    echo "Playing $station"
    notify-send "Playing $station"
    vlc --random --quiet --qt-start-minimized --playlist-autostart $station
    git pull
end
