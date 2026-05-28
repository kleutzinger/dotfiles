#!/usr/bin/env bash
set -euo pipefail

REPO="TwilitRealm/dusklight"
DEST="$HOME/Desktop"
OUTPUT="$DEST/Dusk-latest-x86_64.AppImage"

echo "Fetching latest release info..."
RELEASE=$(curl -s "https://api.github.com/repos/$REPO/releases/latest")
TAG=$(echo "$RELEASE" | grep '"tag_name"' | cut -d'"' -f4)
VERSION="${TAG#v}"

URL="https://github.com/$REPO/releases/download/$TAG/Dusklight-$TAG-linux-x86_64.AppImage"

echo "Latest version: $TAG"
echo "Downloading to $OUTPUT..."
wget -O "$OUTPUT" "$URL"
chmod a+x "$OUTPUT"
echo "Done: $OUTPUT"
