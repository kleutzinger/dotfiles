#!/usr/bin/env sh
kitty\
   -o background=#000000 \
   -o initial_window_width=1100 \
   -o initial_window_height=600 \
   -o remember_window_size=no \
   -o font_size=9 \
   -o hide_window_decorations=no \
   "$@"
