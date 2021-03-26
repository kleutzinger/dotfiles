#!/usr/bin/env sh

# format python contained inside clipboard
# overwrite clipbord with stored version

#black -c (xsel -ob) | xsel -ib
#black -c (xsel -ob) | xsel -ib
#xdotool getactivewindow key ctrl+v
#set pyfile (mktemp --suffix .py)
xdotool getactivewindow key ctrl+c
sleep 0.2
xsel -ob | black - | xsel -ib
sleep 0.2
xdotool getactivewindow key ctrl+v
