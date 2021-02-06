#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Please supply an image"
    exit 1
fi

echo "converting $1"

convert "$1" -resize 16x16    icon16.png
convert "$1" -resize 32x32    icon32.png
convert "$1" -resize 48x48    icon48.png
convert "$1" -resize 64x64    icon64.png
convert "$1" -resize 128x128  icon128.png

echo "done"