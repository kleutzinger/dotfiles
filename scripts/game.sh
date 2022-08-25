#!/usr/bin/env sh
pushd ~/gits/find-classic-games.git
source $HOME/.virtualenvs/find-classic-games-git/bin/activate
python fuzzy_launch.py "$@"
deactivate
popd
