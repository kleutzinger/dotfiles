#!/usr/bin/env bash

until p=$(pidof xfsettingsd)
do
        sleep 1
done
sleep 1
sxhkd &
notify-send "started sxhkd"
