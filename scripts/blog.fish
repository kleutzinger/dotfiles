#!/usr/bin/env fish
# start a lektor instance and open browser
set BLOG_DIR ~/lektor
set LEKTOR_PORT 9001
alias lektor '/home/kevin/.virtualenvs/lektor-fork/bin/python -m lektor'
# ping cannot check ports, use curl
curl localhost:$LEKTOR_PORT -s > /dev/null
if test $status -eq 0
    echo "already running, opening new tab"
    $BROWSER "http://localhost:$LEKTOR_PORT"
    exit 0
end

# start up server
cd $BLOG_DIR
contains "deploy" $argv && lektor build && lektor deploy && exit 0
lektor server -p $LEKTOR_PORT --browse-subpage 'admin/edit?path=%2Fblog'
