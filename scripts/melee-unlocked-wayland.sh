#!/bin/sh
# Re-wrap Melee Unlocked's game binaries so the game window runs on native Wayland
# while the settings window (--settings-window) stays on X11 like the launcher.
# Run this after the built-in updater replaces melee_source (it removes the wrapper).
#
# Usage: melee-unlocked-wayland.sh [game-dir]   (default: ~/Games/MeleeUnlocked-0.9.220)
# Undo:  cd <game-dir> && mv melee_source.real melee_source && mv melee_source_compat.real melee_source_compat
set -eu
D="${1:-$HOME/Games/MeleeUnlocked-0.9.220}"
[ -d "$D" ] || { echo "no such game dir: $D" >&2; exit 1; }

for n in melee_source melee_source_compat; do
  f="$D/$n"
  [ -f "$f" ] || continue
  if ! head -c 4 "$f" | grep -q 'ELF'; then
    echo "$n: already wrapped"
    continue
  fi
  mv -f "$f" "$f.real"
  tmp="$f.wrap.$$"
  cat > "$tmp" <<WRAP
#!/bin/sh
# Wrapper: the game uses Wayland; the settings window (--settings-window) stays on X11.
# Managed by ~/scripts/melee-unlocked-wayland.sh
case " \$* " in
  *" --settings-window "*) ;;
  *) export SDL_VIDEODRIVER=wayland ;;
esac
exec "\$(dirname "\$0")/$n.real" "\$@"
WRAP
  chmod +x "$tmp"
  mv -f "$tmp" "$f"
  echo "$n: wrapped (new binary moved to $n.real)"
done
