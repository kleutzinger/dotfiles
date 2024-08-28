function padpost --description 'post clipboard to pad. run padget on other end'
  set CLIP (xsel -ob | python -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  curl -H "Content-Type: application/json" -d "{\"message\": $CLIP}" https://pad.kevbot.xyz/api
end
