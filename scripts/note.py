#!/usr/bin/env python3
"""
porting note.sh to python. 

USAGE:
    ./note.py or python note.py

ARGS:
    [e]dit # edit this python script
    [m]ovie # insert movie template

TODO:
    [x] check env NOTE_DIR
    [x] `mkdir -p "$NOTE_DIR"`

    [x] go to minus day
        - [ ] add cli arg for this
    [x] select by content? search headers?
    [ ] launch check_notes.fish
    [ ] search headers (# HEADER)
        [ ] select notes containing header
    [x] movie template
        - themes, who should watch it,
        - access tmdb api? movies.kevbot.xyz api?
    [ ] upload
        - note u or note s (upload / synchronize)
    [ ] titles?
    [ ] named notes. like `note.py vim`
    [ ] fish shell completion generation
        [ ] move templates to dict?

https://stackoverflow.com/questions/26216875/how-to-handle-cli-subcommands-with-argparse
"""
import argparse
import datetime
import getpass
import glob
import os
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
    "\n## Themes\n\n## Characters\n\n## Memorable Parts\n\n## Reminded Me of\n\n"
)


def main():
    verify_env()
    os.chdir(NOTE_DIR)
    if len(sys.argv) == 1:
        # no additional arguments
        filename = get_note_path()
        print(f"opening {filename}")
        open_note(filename)
    else:
        argcmd = sys.argv[1]
        if argcmd == "e":
            # edit this source code
            subprocess.run(f"{EDITOR} {__file__}", shell=True)
        if argcmd.startswith("m"):
            # edit this source code
            open_note(get_note_path(), MOVIE_TEMPLATE)
        if argcmd == ("p"):
            # print today's note path
            print(os.path.abspath(get_note_path()))


def verify_env():
    "verify env vars are set. create certain directories as well"
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
    "open note in editor. creates file on open if not existing"
    with open(path, "a+") as f:
        if append_template:
            f.write(append_template)
    subprocess.run(f"{EDITOR} {path}", shell=True)


def get_note_path(days_ago=0):
    "get today's note path. or get it from X days ago"
    timestamp = time.time() - (3600 * MIDNIGHT_HOUR_SHIFT) - (days_ago * 3600 * 24)
    at_date = datetime.date.fromtimestamp(timestamp)
    filename = at_date.strftime(NOTE_STRFTIME) + NOTE_EXT
    return filename


def get_note_list():
    "return all note filenames [ 1.md, 2.md, ... ]"
    note_list = list(sorted(glob.glob("*.md")))
    return note_list


def new_movie(note_path):
    "add movie template to a note"
    # note should already exist?
    # call api?
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
