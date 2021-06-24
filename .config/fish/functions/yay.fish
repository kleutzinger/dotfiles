function yay
    pushd $HOME
    if test -n "$VIRTUAL_ENV"
        echo "temporarily disabling venv $VIRTUAL_ENV"
        set TEMP_VENV $VIRTUAL_ENV
        deactivate
    end
    command paru $argv
    if test -n $TEMP_VENV
        source $TEMP_VENV/bin/activate.fish
    end
    popd
end

