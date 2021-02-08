#!/usr/bin/env sh
pushd ~/gits/find-classic-games.git
source .venv/bin/activate
python fuzzy_launch.py
deactivate
popd
