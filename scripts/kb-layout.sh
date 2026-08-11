#!/usr/bin/env bash
# Toggle KDE Plasma's keyboard layout by reordering LayoutList/VariantList
# in kxkbrc and asking KConfig to notify listeners, instead of switching the
# active XKB group in place. Games (esp. Proton/Wine via XWayland) often
# ignore group-switch events but always pick up a reordered/reloaded layout,
# since it forces a real keymap rebuild - the same thing System Settings does
# when you drag a layout to the top of the list.
#
# Usage: kb-layout.sh [colemak|qwerty|toggle]
#   (no args = toggle)

set -euo pipefail

KXKBRC="kxkbrc"
GROUP="Layout"

current_variants() {
    kreadconfig6 --file "$KXKBRC" --group "$GROUP" --key VariantList
}

set_primary() {
    local target="$1" # "colemak" or "qwerty"
    local variants
    if [[ "$target" == "colemak" ]]; then
        variants="colemak,"
    else
        variants=",colemak"
    fi
    kwriteconfig6 --file "$KXKBRC" --group "$GROUP" --key VariantList "$variants" --notify
    notify-send -t 1500 "Keyboard layout" "${target^} is now primary"
}

mode="${1:-toggle}"

case "$mode" in
    colemak|qwerty)
        set_primary "$mode"
        ;;
    toggle)
        if [[ "$(current_variants)" == "colemak," ]]; then
            set_primary "qwerty"
        else
            set_primary "colemak"
        fi
        ;;
    *)
        echo "Usage: $(basename "$0") [colemak|qwerty|toggle]" >&2
        exit 1
        ;;
esac
