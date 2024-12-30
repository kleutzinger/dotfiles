function food --description 'submit or check food I just ate'
    set TEMP_HTML (mktemp --suffix .html)
    # If no arguments are provided, print today's food journal
    if test (count $argv) -eq 0
        http -f --pretty=none get 127.0.0.1:37840/custom/food >$TEMP_HTML
        # else add a new food entry
    else
        http -f --pretty=none post 127.0.0.1:37840/custom/food --body food="$argv" >$TEMP_HTML
    end
    # check if html2md is installed
    if type -q html2md
        cat $TEMP_HTML | html2md --in
    else
        cat $TEMP_HTML
    end
end
