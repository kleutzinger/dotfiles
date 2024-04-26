function pkg_url_open --description "open package's source code or homepage"
    # choose package, wait for EOF to pipe
    set pkg (yay -Slaq | tac | tac | fzf)
    set url (yay -Gp $pkg | grep '^url=' | grep -oP "(?<=\")[^\"]+(?=\")|(?<=').*(?=')")
    echo $url
    python -m webbrowser -t "$url"
end
