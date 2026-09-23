#!/usr/bin/env bash
# Re-exports atuin's legacy synced dotfiles vars (atuin dotfiles var list)
# as KEY<TAB>VALUE lines, one per line, for atuin_load_dotfiles_vars.fish to consume.
# Atuin itself stopped applying these to the shell as of v18.23.0.

lines="$(atuin dotfiles var list --exports-only 2>/dev/null)"
[ -z "$lines" ] && exit 0

keys=$(printf '%s\n' "$lines" | sed -n 's/^export \([A-Za-z_][A-Za-z0-9_]*\)=.*/\1/p')

eval "$lines" 2>/dev/null

for k in $keys; do
    printf '%s\t%s\n' "$k" "${!k}"
done
