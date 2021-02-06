#! /usr/bin/env fish
# run simple window manager commands on active window
# moving is really too slow and buggy to rely on
# perhaps I should convert this file to `.sh`?
set valid_args 'max' 'min' 'move_next' 'move_prev'


if not contains $argv[1] $valid_args
    set msg (string join ', ' $valid_args)
    echo "required arguments: [$msg]"
    exit 1
end

if test $argv[1] = 'max'
    xdotool windowsize (xdotool getactivewindow) 100% 100%
    exit 0
end

if test $argv[1] = 'min'
    xdotool windowminimize (xdotool getactivewindow)
    exit 0
end

if test $argv[1] = 'move_next'
    set MAXD ( wmctrl -d | tail -n 1 | awk '{print $1}' )
    set CURD ( wmctrl -d | awk '{ if ($2 == "'\*'") print $1}' )
    set TOD ( math "($CURD + 1) % ($MAXD + 1)" )
    wmctrl -r :ACTIVE: -t $TOD; wmctrl -s $TOD
    exit 0
end

if test $argv[1] = 'move_prev'
    set MAXD ( wmctrl -d | tail -n 1 | awk '{print $1}' )
    set CURD ( wmctrl -d | awk '{ if ($2 == "'\*'") print $1}' )
    set TOD ( math "($CURD - 1) % ($MAXD + 1)" )
    if test $TOD -eq "-1"
        set TOD $MAXD
    end
    wmctrl -r :ACTIVE: -t $TOD; wmctrl -s $TOD
    exit 0
end

