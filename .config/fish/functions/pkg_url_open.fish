function pkg_url_open --description "open package's source code or homepage"
    set url (pacman -Qi $argv | grep URL | grep -oE '[^ ]+$')
    echo $url
    python -m webbrowser -t "$url"
end
