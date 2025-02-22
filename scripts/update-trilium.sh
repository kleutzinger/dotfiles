#!/usr/bin/env bash
# downloads the latest release of trilium-next from
# https://github.com/TriliumNext/Notes/releases/latest
# and installs it in the home directory
set -e
set -x

TAG="v0.92.2-beta"

# this is the dir in the home directory where the trilium-next will be installed
DIRNAME=trilium-next
DL_URL="https://github.com/TriliumNext/Notes/releases/download/$TAG/TriliumNextNotes-$TAG-linux-x64.zip"

cd $(mktemp --directory --suffix=trilium-update)
wget --verbose $DL_URL
unzip *.zip
rm *.zip
rm -rf ~/$DIRNAME
mv * ~/trilium-next
# ensure symlink to ~/.local/bin/trilium
rm -f ~/.local/bin/trilium
ln -sf ~/$DIRNAME/trilium ~/.local/bin/trilium
