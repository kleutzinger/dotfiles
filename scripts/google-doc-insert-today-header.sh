#!/usr/bin/env sh

# while in google docs, insert today's date as a header

# google docs shortcut to insert header
xdotool getactivewindow key 'ctrl+alt+1'
sleep 0.2
xdotool type '@today'
sleep 0.2
xdotool key Return
sleep 0.2
xdotool key Return
