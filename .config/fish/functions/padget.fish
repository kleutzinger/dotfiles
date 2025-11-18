function padget --description 'get message from pad.kevbot.xyz service and copy to clipboard'
    # get message
    set message (curl --silent https://pad.kevbot.xyz/api | jq -r '.message')
    # save to clipboard (cross-platform)
    if test (uname) = Darwin
        echo -n $message | pbcopy
    else
        echo $message | xsel -ib
    end
    set short_message (echo "$message" | head -c 20)
    # notify (cross-platform)
    if test (uname) = Darwin
        osascript -e "display notification \"copied to clipboard: $short_message\" with title \"padget\""
    else
        notify-send padget "copied to clipboard: $short_message"
    end
end
