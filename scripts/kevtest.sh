#!/bin/bash

set -x
set -e

cd $HOME/scripts/kevtests/

uvx --with psutil pytest
