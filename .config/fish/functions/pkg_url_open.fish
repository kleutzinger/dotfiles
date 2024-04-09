function pkg_url_open --description "open package's source code or homepage"
    set pkg (yay -Slaq |  fzf)
    set url (yay -Gp $pkg | grep '^url=' | grep -oP '(?<=\")[^\"]+(?=\")')
    echo $url
    python -m webbrowser -t "$url"
end
