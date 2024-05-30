function gitpullall --description 'cd into all directories in the current directory and pull from git'
    for dir in */
        if test -d $dir/.git
            echo "Pulling from $dir"
            cd $dir
            # check if hub is installed
            if type -q hub
                hub sync
            else
                git pull
            end
            cd ..
        end
    end
end
