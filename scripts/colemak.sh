#!/usr/bin/env bash

until p=$(pidof xfsettingsd)
do
        sleep 1
done
sleep 1
setxkbmap us -variant colemak -option ctrl:swap_lalt_lctl
notify-send "set colemak"
