#!/usr/bin/env bash
# downloads the latest release of trilium-next from
# https://github.com/TriliumNext/Notes/releases/latest
# and installs it in the home directory
set -e
set -x

# this is the dir in the home directory where the trilium-next will be installed
DIRNAME=trilium-next

cd $(mktemp --directory --suffix=trilium-update)
dra download TriliumNext/Notes --tag v0.91.3-beta --automatic
unzip *.zip
rm *.zip
rm -rf ~/$DIRNAME
mv * ~/trilium-next
# ensure symlink to ~/.local/bin/trilium
rm -f ~/.local/bin/trilium
ln -sf ~/$DIRNAME/trilium ~/.local/bin/trilium
