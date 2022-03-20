#!/usr/bin/env sh

# while in google docs, insert today's date as a header

WEEKDAY=$(date +"%A")

# google docs shortcut to insert header
xdotool getactivewindow key 'ctrl+alt+1'
sleep 0.3
xdotool type '@today'
sleep 0.3
xdotool key Return
sleep 0.3
xdotool type " ($WEEKDAY)"
sleep 0.3
xdotool key Return