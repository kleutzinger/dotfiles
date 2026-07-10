function p --description paste
    if type -q pbpaste
        pbpaste
    else if test -n "$WAYLAND_DISPLAY"; and type -q wl-paste
        wl-paste --no-newline
    else
        xsel -ob
    end
end
