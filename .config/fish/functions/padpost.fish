function padpost --description 'post clipboard to pad. run padget on other end'
    # get clipboard (cross-platform)
    if test (uname) = Darwin
        set CLIP (pbpaste | json_escape)
    else
        set CLIP (xsel -ob | json_escape)
    end
    curl -H "Content-Type: application/json" -d "{\"message\": $CLIP}" https://pad.kevbot.xyz/api
end
