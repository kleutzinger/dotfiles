#!/usr/bin/env bash
# downloads the latest release of trilium-next from
# https://github.com/TriliumNext/Notes/releases/latest
# and installs it in the home directory
set -e
set -x

TAG=$(gh release list --repo TriliumNext/Notes --json tagName,publishedAt --jq '.[] | .tagName + "      " + .publishedAt' | fzf | awk '{print $1}')

# this is the dir in the home directory where the trilium-next will be installed
INSTALL_DIR=trilium-next
DL_URL="https://github.com/TriliumNext/Notes/releases/download/$TAG/TriliumNextNotes-$TAG-linux-x64.zip"

cd $(mktemp --directory --suffix=trilium-update)
wget --verbose $DL_URL
unzip *.zip
rm *.zip
rm -rf ~/$INSTALL_DIR
mv * ~/trilium-next
# ensure symlink to ~/.local/bin/trilium
rm -f ~/.local/bin/trilium
ln -sf ~/$INSTALL_DIR/trilium ~/.local/bin/trilium
