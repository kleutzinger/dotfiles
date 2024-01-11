function __auto_venv --on-variable PWD --description "Automatically activate python venv"
    set -l venv_name (dirs | tr . + | tr '/' + | tr '~' +)

    if test -d $HOME/.virtualenvs/$venv_name
        echo "+ ~/.virtualenvs/$venv_name/" 1>&2
        source $HOME/.virtualenvs/$venv_name/bin/activate.fish
    end
    # if homedir disable venv
    if test $PWD = $HOME && test -n "$VIRTUAL_ENV"
        echo "deactivating $VIRTUAL_ENV" 1>&2
        deactivate
    end
end


# maybe I should port this to python
