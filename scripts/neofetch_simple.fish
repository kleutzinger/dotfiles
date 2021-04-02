#!/usr/bin/env fish
cat (neofetch --memory_display --disable memory uptime --stdout | head -n 16 | psub) (echo -e 'Memory: 19745MiB\nEditor: neovim' | psub)
