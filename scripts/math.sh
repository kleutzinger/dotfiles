#!/usr/bin/env bash
output=$(echo "$(xclip -o)" | bc) # take the X clipboard and run it through bc
sleep 0.2s # wait before continuing or else this won't work
xdotool key BackSpace # clear the selection
echo $output | xclip -i # write the output to the X clipboard
xdotool click 2 # paste the result by clicking the middle button

