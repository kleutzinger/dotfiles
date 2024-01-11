function venv --argument-names python_version --description 'Create virtualenv named the same as current directory'
    # it would be cool to add -e flag to make a symlink
    # z worker
    # venv -e
    #    does fzf for existing venvs
    #    finds existing venvs
    #    symlinks cur dir to existing venv
    set -l python_bin

    if not test -n "$python_version"
        # Use default python version set by asdf
        #set python_bin (asdf which python)
        set python_bin (which python)
    else
        set python_bin $ASDF_DIR/installs/python/$python_version/bin/python
        echo "activating $python_bin"
    end

    set -l venv_name (dirs | tr . + | tr '/' + | tr '~' +)

    if not test -e $python_bin
        echo "Python version `$python_version` is not installed."
        return 1
    end

    echo Creating virtualenv `$venv_name`
    $python_bin -m venv $HOME/.virtualenvs/$venv_name
    source $HOME/.virtualenvs/$venv_name/bin/activate.fish
    echo `$venv_name`  activated

    if test -e 'requirements.txt'
        echo 'requirements.txt detected, install?'
        if read_confirm
            python -m pip install -r requirements.txt
        end
    end
end

