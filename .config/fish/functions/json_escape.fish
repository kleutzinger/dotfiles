function json_escape --description "Escape text for use in JSON"
    python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
end
