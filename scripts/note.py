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
8. upload
    - note u or note s (upload / synchronize)
9. titles?
10. named notes. like `note.py vim`
"""
import argparse
import datetime
import getpass
import glob
import os
import shlex
import shutil
import subprocess
import sys
import time

EDITOR = os.getenv("EDITOR") or "gedit"
if getpass.getuser() == "kevin":
    EDITOR = "nvim '+normal G\$'"

# how many hours after midnight do days roll over (5 am default)
MIDNIGHT_HOUR_SHIFT = 5
# note path = NOTE_DIR/NOTE_STRFTIME.NOTE_EXT
NOTE_DIR = os.getenv("NOTE_DIR")
NOTE_STRFTIME = "%Y-%m-%d"
NOTE_EXT = ".md"
MOVIE_TEMPLATE = (
    "\n## Themes\n\n## Characters\n\n##Memorable Parts\n\n## Reminded Me of\n\n"
)


def main():
    verify_env()
    os.chdir(NOTE_DIR)
    if len(sys.argv) == 1:
        filename = get_note_path()
        print(f"opening {filename}")
        open_note(filename)
    else:
        argcmd = sys.argv[1]
        if argcmd == "e":
            # edit this source code
            os.system(f"{EDITOR} {__file__}")


def verify_env():
    if not NOTE_DIR:
        print("please set NOTE_DIR environment variable, exiting")
        exit(1)

    if not os.path.exists(NOTE_DIR):
        print("creating ${NOTE_DIR}")
        os.makedirs(NOTE_DIR)

    editor_loc = shutil.which(EDITOR.split(" ")[0])
    if not editor_loc:
        print(f"invalid EDITOR:\n{EDITOR}")
        print("please set EDITOR environment variable or edit this script")


def open_note(path, append_template=""):
    with open(path, "a+") as f:
        if append_template:
            f.write(append_template)
    os.system(f"{EDITOR} {path}")


def get_note_path(days_ago=0):
    # find if note exists
    # create if not
    # notes_ago ?
    timestamp = time.time() - (3600 * MIDNIGHT_HOUR_SHIFT) - (days_ago * 3600 * 24)
    at_date = datetime.date.fromtimestamp(timestamp)
    filename = at_date.strftime(NOTE_STRFTIME) + NOTE_EXT
    return filename

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
    # argumets = parse_arguments()
    main()
