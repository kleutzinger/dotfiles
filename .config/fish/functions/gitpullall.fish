function gitpullall --description 'cd into all directories in the current directory and pull from git'
    for dir in */
        if test -d $dir/.git
            echo "Pulling from $dir"
            cd $dir
            git pull
            cd ..
        end
    end
end
