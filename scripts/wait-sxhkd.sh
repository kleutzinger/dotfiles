#!/usr/bin/env bash

until p=$(pidof xfsettingsd)
do
        sleep 1
done
sleep 4
sxhkd &
notify-send "started sxhkd"
