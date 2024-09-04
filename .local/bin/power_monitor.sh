#! /bin/bash

# from https://kobusvs.co.za/blog/power-profile-switching/
# or   https://archive.is/wip/Vh4ux

BAT=$(echo /sys/class/power_supply/BAT*)
BAT_STATUS="$BAT/status"
BAT_CAP="$BAT/capacity"
LOW_BAT_PERCENT=95

AC_PROFILE="performance"
BAT_PROFILE="performance"
LOW_BAT_PROFILE="power-saver"

# wait a while if needed
[[ -z $STARTUP_WAIT ]] || sleep "$STARTUP_WAIT"

# start the monitor loop
prev=0

while true; do
	# read the current state
	if [[ $(cat "$BAT_STATUS") == "Discharging" ]]; then
		if [[ $(cat "$BAT_CAP") -gt $LOW_BAT_PERCENT ]]; then
			profile=$BAT_PROFILE
		else
			profile=$LOW_BAT_PROFILE
		fi
	else
		profile=$AC_PROFILE
	fi

	# set the new profile
	if [[ $prev != "$profile" ]]; then
		echo setting power profile to $profile
		powerprofilesctl set $profile
    notify-send --expire-time=2000 "Power profile set to $profile"
	fi

	prev=$profile

	# wait for the next power change event
	inotifywait -qq "$BAT_STATUS" "$BAT_CAP"
done
