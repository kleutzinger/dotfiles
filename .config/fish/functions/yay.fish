# Defined in /tmp/fish.BrAOrq/yay.fish @ line 2
function yay
    if test (uname) = "Darwin"  # we're on mac
        brew update
        brew upgrade
        return
    end
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
