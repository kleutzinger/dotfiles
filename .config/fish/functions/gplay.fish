function gplay --description 'clone a git repo to a temp dir'
    cd (mktemp --directory --suffix=.git)
    git clone $argv
    cd (ls)
end
