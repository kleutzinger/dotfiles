#!/usr/bin/env bash
youtube-dl -x  -o  "%(playlist_index)s_%(title)s.%(ext)s" "$1"
