#!/bin/bash

set -ex

TEMPFILE=$(mktemp)
xsel -ob > $TEMPFILE
nvim -c "set nofixendofline" $TEMPFILE
cat $TEMPFILE | xsel -ib

