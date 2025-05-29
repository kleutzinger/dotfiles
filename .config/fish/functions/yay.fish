# Defined in /tmp/fish.BrAOrq/yay.fish @ line 2
function yay
    pushd $HOME/Downloads
    if test -n "$VIRTUAL_ENV"
        set -l TEMP_VENV "$VIRTUAL_ENV"
        deactivate
    end
    command yay $argv
    if test -n "$TEMP_VENV"
        source $TEMP_VENV/bin/activate.fish
    end
    popd
end
