function pkg_owns_file --description 'Find the package owning a file'
    set -l file $argv[1]

    # Checking if the file exists
    if test -e $file
        # Using `pacman` to query the package
        set -l pkg (pacman -Qo $file)

        # Extracting the package name from the output
        set -l pkg_name (echo $pkg | cut -d' ' -f5-)

        # Printing the result
        echo "Package owning $file: $pkg_name"
    else
        echo "$file does not exist."
    end

end
