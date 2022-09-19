#!/usr/bin/sh

# fuzzy search open windows, bring to front

xdotool search "$(wmctrl -l | awk '{$3=""; $2=""; $1=""; print $0}' | dmenu -i -l 20)" windowactivate

