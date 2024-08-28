function padpost --description 'post clipboard to pad. run padget on other end'
  set CLIP (xsel -ob | json_escape)
  curl -H "Content-Type: application/json" -d "{\"message\": $CLIP}" https://pad.kevbot.xyz/api
end
