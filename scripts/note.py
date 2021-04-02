#!/usr/bin/env python3
"""
porting note.sh to python. 

USAGE:
    ./note.py or python note.py

1. check env NOTE_DIR
2. `mkdir -p "$NOTE_DIR"`
3. $EDITOR "$NOTE_DIR/$(date --date="5 hours ago" +'%Y-%m-%d').md"
4. go to minus day
    - python note.py -2
        - two days ago
5. select by content? search headers?
6. launch check_notes.fish
7. movie template
    - themes, who should watch it,
    - access tmdb api? movies.kevbot.xyz api?
"""
import argparse
import os
import glob
import time
import datetime
import sys
import subprocess

MOVIE_TEMPLATE = "## Themes\n\n## Characters\n\n ## Reminded Me of\n\n"
EDITOR = "nvim '+normal G\$'" or os.getenv("EDITOR") or "nvim"
# how many hours after midnight do days roll over (5 am default)
MIDNIGHT_HOUR_SHIFT = 5
NOTE_DIR = os.getenv("NOTE_DIR")

if not NOTE_DIR:
    print("please set NOTE_DIR environment variable")
    exit(1)

if not os.path.exists(NOTE_DIR):
    os.makedirs(NOTE_DIR)


def main():
    os.chdir(NOTE_DIR)
    if len(sys.argv) == 1:
        print("opening today's note")
        open_note()
    else:
        print("too many arguments?")
        exit(1)


def open_note(days_ago=0):
    # find if note exists
    # create if not
    # notes_ago ?
    timestamp = time.time() - (3600 * MIDNIGHT_HOUR_SHIFT) - (days_ago * 3600 * 24)
    at_date = datetime.date.fromtimestamp(timestamp)
    filename = at_date.strftime("%Y-%m-%d") + ".md"
    os.system(f"{EDITOR} {filename}")

    # note_list = sorted(glob.glob("*.md"))
    # edit_note(note_list[-1])
    # pass


def new_movie(note_path):
    "add movie template to a note"
    # note should already exist?
    # call api?
    pass


def get_notes():
    pass


def parse_arguments():
    "handle cli flags like -d"
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", required=False, type=int, help="how many days ago")
    parser.add_argument("-s", required=False, type=str, help="search a thing")
    parser.add_argument("-c", required=False, type=str, help="check notes .fish")
    args = parser.parse_args()


if __name__ == "__main__":
    argumets = parse_arguments()
    main()
