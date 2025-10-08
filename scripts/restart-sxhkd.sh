#!/usr/bin/env bash

if pgrep -x sxhkd > /dev/null; then
    pkill -USR1 -x sxhkd
    notify-send "reloaded sxhkd"
else
    sxhkd &
    notify-send "started sxhkd"
fi

