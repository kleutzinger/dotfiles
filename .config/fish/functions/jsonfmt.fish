function jsonfmt --description 'format json files in place'
    for FILE in $argv
        cat $FILE | jq | sponge $FILE
    end
end
