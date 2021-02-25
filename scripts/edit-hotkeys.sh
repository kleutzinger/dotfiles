#!/bin/sh
mini-kitty.sh -o startup_session=hotkey-nvim.kitty.conf
pkill -usr1 -x sxhkd; notify-send -t 1500 'Reloaded config'
