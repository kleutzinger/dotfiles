function cdv -d "change directory, and activate virtualenvs, if available"
    # first and foremost, change directory
    builtin cd $argv

    # find a parent git directory
    if git rev-parse --show-toplevel
        set gitdir (realpath (git rev-parse --show-toplevel))
    else
        set gitdir ""
    end

    # if that directory contains a virtualenv in a ".venv" directory, activate it
    if test \( -z "$VIRTUAL_ENV" -o "$VIRTUAL_ENV" != "$gitdir/.venv" \) -a -f "$gitdir/.venv/bin/activate.fish"
        source $gitdir/.venv/bin/activate.fish
    end

    #   # deactivate an active virtualenv if not int a git directory with an ".env"
    #   if test -n "$VIRTUAL_ENV" -a "$VIRTUAL_ENV" != "$gitdir/.venv"
    #           deactivate
    #   end
end
