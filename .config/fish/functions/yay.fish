function yay
    if string match -r 'rescale' (pwd) > /dev/null
        echo "cannot run yay inside $HOME/rescale/ subfolder"
        return 1
    end
    if test -n "$VIRTUAL_ENV"
        echo "cannot run yay inside virtual env $VIRTUAL_ENV"
        return 1
    end
    command yay $argv
end

