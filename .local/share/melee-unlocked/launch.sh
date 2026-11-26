#!/bin/sh
# Starts the Melee Unlocked launcher on X11 after re-wrapping the game for Wayland.
D=$(ls -td "$HOME"/Games/MeleeUnlocked-*/MeleeUnlocked 2>/dev/null | head -n 1 | xargs -r -d '\n' dirname)
[ -n "$D" ] || exit 1
"$HOME/scripts/melee-unlocked-wayland.sh" "$D" || true
cd "$D" && SDL_VIDEODRIVER=x11 exec ./MeleeUnlocked "$@"
