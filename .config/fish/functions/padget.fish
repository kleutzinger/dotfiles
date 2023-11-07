function padget --description 'get message from pad.kevbot.xyz service and copy to clipboard'
    # get message
    set message (curl --silent https://pad.kevbot.xyz/api | jq -r '.message')
    # save to clipboard
    echo $message | xsel -ib
    set short_message (echo "$message" | head -c 20)
    notify-send padget "copied to clipboard: $short_message"
end
