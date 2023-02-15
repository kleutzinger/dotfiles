#!/usr/bin/env sh
DIRNAME=find-and-play-classic-videogames
pushd ~/gits/$DIRNAME
source $HOME/.virtualenvs/DIRNAME/bin/activate
python fuzzy_launch.py "$@"
deactivate
popd
