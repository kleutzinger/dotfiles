function pkg_url_open --description "open package's source code or homepage"
    if test -z $argv
        set argv (yay -Q | awk '{print $1}' | fzf)
    end
    set url (pacman -Qi $argv | grep URL | grep -oE '[^ ]+$')
    echo $url
    python -m webbrowser -t "$url"
end
