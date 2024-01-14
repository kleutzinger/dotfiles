function padpost --description 'post clipboard to pad. run padget on other end'
    http post https://pad.kevbot.xyz/api message="$(xsel -ob)"
end
