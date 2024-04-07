function recent_played_vlc --description 'Get the first URL from the recent played list of VLC'
    set recent_mrl_list (grep -oP "(?<=list=).*" $HOME/.config/vlc/vlc-qt-interface.conf)
    set -l first_url (string split ", " $recent_mrl_list)[1]
    # check for --file flag
    if test -n "$argv"
        if test "$argv[1]" = --file
            echo $first_url | python -c "import sys; from urllib.parse import unquote; print(unquote(sys.stdin.read().removeprefix('file://')));"
            return
        end
    else
        echo $first_url
    end
end
