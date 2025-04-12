#!/usr/bin/env bash

# detect linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux detected"
    sh <(curl -L https://nixos.org/nix/install) --daemon
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "MacOS detected"
    curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | \
      sh -s -- install --determinate
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

nix-channel --add https://nixos.org/channels/nixpkgs-unstable && nix-channel --update
echo "Nix installed successfully, now run nvim"
