function supercd
    # Get the path argument or default to the current directory
    set path (or $argv[1] .)

    # Recursively list all directories using fd, then sort them, and use fzf to select a directory
    set selected_dir (fd --hidden --no-ignore --type d . $path | awk '{ print length($0), $0 }' | sort -n | cut -d' ' -f2- | fzf --preview 'ls -la --color=always {}')

    # If a directory was selected, change to that directory
    if test -n "$selected_dir"
        cd "$selected_dir"
        echo "Changed directory to: $selected_dir"
    else
        echo "No directory selected."
    end
end
