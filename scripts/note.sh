#!/usr/bin/env bash

set -euo pipefail

if [ -z ${NOTE_DIR+x} ]; then
  echo "Error: Please configure and export NOTE_DIR environment variable."
  exit 1
fi

function usage() {
  echo "Usage: note.sh [action]"
  echo
  echo "  actions:"
  echo "    grep [pattern]"
}

mkdir -p "$NOTE_DIR"

if [ $# -eq 0 ]; then
    # days roll over at 5:00 am rather than midnight
    $EDITOR "$NOTE_DIR/$(date --date="5 hours ago" +'%Y-%m-%d').md"
else
  case $1 in
    grep)
      grep -i -r --color "$2" "$NOTE_DIR"
      ;;
    *)
      usage
      ;;
  esac
fi
