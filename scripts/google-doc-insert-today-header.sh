#!/usr/bin/env sh

# while in google docs, insert today's date as a header
# example:

# Dec 12, 2022 (Mon)<newline>

WEEKDAY=$(date +"%a")

# google docs shortcut to insert header
xdotool getactivewindow key 'ctrl+alt+1'
sleep 0.3
# mousing over the `@` popup disrupts the selection
xdotool mousemove 0 0
# xdotool needs qwerty idk why
setxkbmap us -option ctrl:swap_lalt_lctl
xdotool type '@today'
sleep 1
xdotool key Return
sleep 0.3
xdotool type " ($WEEKDAY)"
sleep 0.3
# back to colemak
setxkbmap us -variant colemak -option ctrl:swap_lalt_lctl
xdotool key Return
