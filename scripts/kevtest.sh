#!/bin/bash

set -x
set -e

cd $HOME/scripts/kevtests/

$HOME/.virtualenvs/++scripts+kevtests/bin/pytest --verbose
