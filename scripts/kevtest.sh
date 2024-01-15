#!/bin/bash

set -x
set -e

cd $HOME/scripts/kevtests/

# forwards all arguments to pytest
#
$HOME/.virtualenvs/++scripts+kevtests/bin/pytest $@
