#!/usr/bin/env fish
# start a lektor instance and open browser
set BLOG_DIR ~/lektor/kev-project-lektor
set LEKTOR_PORT 9001
# ping cannot check ports, use curl
curl localhost:$LEKTOR_PORT -s > /dev/null
if test $status -eq 0
    echo "already running, opening new tab"
    $BROWSER "http://localhost:$LEKTOR_PORT"
    exit 0
end

# start up server
cd $BLOG_DIR
source ../.venv/bin/activate.fish
lektor server -p $LEKTOR_PORT --browse
