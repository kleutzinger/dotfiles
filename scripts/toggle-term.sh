#!/bin/sh
# toggles a kitty terminal instance
# bind this to a hotkey
# accepts the --new-window flag to open a new window inside the terminal

# todo: add --new-tab to open a new tab altogether

TERMINAL_CMD='kitty -o allow-remote-control=true --listen-on unix:/tmp/kitty'
if [ "$1" = "--new-window" ]; then
	NEW_WINDOW="true"
else
	NEW_WINDOW="false"
fi

kitty_ls="$(kitty @ --to unix:/tmp/kitty ls)"
# if last command exit 1, then no kitty is running
if [ $? -eq 1 ]; then
	$TERMINAL_CMD
	exit 0
fi

window_id=$(echo $kitty_ls | jq -r '.[].platform_window_id')
is_focused=$(echo $kitty_ls | jq -r '.[].is_focused')
if [ "$is_focused" = "true" ] && [ "$NEW_WINDOW" = "false" ]; then
	xdotool windowminimize $window_id
else
	# focus
	xdotool windowactivate $window_id
	if [ "$NEW_WINDOW" = "true" ]; then
		kitty @ --to unix:/tmp/kitty launch --type=window
	fi
fi
