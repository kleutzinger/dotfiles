function recent_played_vlc
    set recent_mrl_list (grep -oP "(?<=list=).*" $HOME/.config/vlc/vlc-qt-interface.conf)
    set -l first_url (string split ", " $recent_mrl_list)[1]
    echo $first_url
end
