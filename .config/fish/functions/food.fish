function food --description 'submit or check food I just ate'
    # If no arguments are provided, print today's food journal
    if test (count $argv) -eq 0
        http -f --pretty=none get 127.0.0.1:37840/custom/food | html2md --in
        return 0
    end
    # else add a new food entry
    http -f --pretty=none post 127.0.0.1:37840/custom/food --body food="$argv" | html2md --in
end
