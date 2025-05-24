#!/usr/bin/env sh
set -ex
DIRNAME=find-and-play-classic-videogames
pushd ~/gits/$DIRNAME
uv run fuzzy_launch.py "$@"
# uv run eel_server.py
popd
