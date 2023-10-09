#!/usr/bin/python3
"""
porting note.sh to python. 

USAGE:
    ./note.py
    python note.py

ARGS:
    e   # (edit)  edit this python script
    m   # (movie) append MOVIE_TEMPLATE to todays note before opening
    p   # (print) print absolute filepath to today's note
    i   # (interactive) choose a note from many previewed options


TODO:
    [x] check env NOTE_DIR
    [x] `mkdir -p "$NOTE_DIR"`

    [x] go to minus day
        - [ ] add cli arg for this
    [x] select by content? search headers?
    [ ] launch check_notes.fish
    [x] figure out only opening single instance of nvim (i use nvim-qt)
    [x] search headers (# HEADER)
    [x] movie template
        - themes, who should watch it,
        - access tmdb api? movies.kevbot.xyz api?
    [ ] upload
        - note u or note s (upload / synchronize)
    [ ] titles?
    [ ] named notes. like `note.py vim`
    [ ] fish shell completion generation
        [ ] move templates to dict?
    [ ] note.py c # paste clipboard contents to note

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

# how many hours after midnight do days roll over (5 am default)
MIDNIGHT_HOUR_SHIFT = 5
# note path = NOTE_DIR/NOTE_STRFTIME.NOTE_EXT
NOTE_DIR = os.getenv("NOTE_DIR") or os.path.join(os.path.expanduser("~"), "notes")
HEADER_STRFTIME = "%Y-%m-%d %a"
NOTE_EXT = ".md"

if getpass.getuser() == "kevin":
    # this is for my own stuff
    NOTE_EXT = ".md"


def get_note_path():
    "get the main note file's path"
    current_year = datetime.datetime.now().year
    return os.path.join(NOTE_DIR, f"note-{current_year}{NOTE_EXT}")


def EDITOR_AT_LINE(line_num=None, note_path=get_note_path()):
    "open a file at a certain line number. if no line number provided, open at bottom"
    if line_num is None:
        # assume bottom of file
        run_cmd = "nvim-qt '+normal " + r"G\$zz ' " + note_path
    else:
        run_cmd = f"nvim-qt '+normal {line_num}" + r"G\$zz' " + note_path
    subprocess.run(run_cmd, shell=True)


def main():
    verify_env()
    os.chdir(NOTE_DIR)
    if len(sys.argv) == 1:
        # no additional arguments
        filename = get_note_path()
        print(f"opening {filename}")
        open_note(filename)
        return
    else:
        argcmd = sys.argv[1]
        if argcmd == "e":
            # edit this source code
            EDITOR_AT_LINE(0, __file__)
            return
        if argcmd.startswith("m"):
            import movie_api

            search_query = input("what movie title?\n")
            template = movie_api.search_to_template(search_query)
            open_note(get_note_path(), None, template)
            return
        if argcmd == "p":
            # print today's note path
            print(os.path.abspath(get_note_path()))
        if argcmd == "i":
            print("have to reimplment this")
            sys.exit(1)
            from iterfzf import iterfzf

            # get a fzf all notes in dir and choose one to edit
            all_mds = []
            for note_filename in glob.glob(os.path.join(NOTE_DIR, f"*{NOTE_EXT}")):
                all_mds.append(note_filename)
            to_edit_filename = iterfzf(sorted(all_mds, reverse=True), preview="cat {}")
            open_note(to_edit_filename)


def verify_env():
    "verify env vars are set. create certain directories as well"
    if not NOTE_DIR:
        print("please set NOTE_DIR environment variable, exiting")
        exit(1)
    if not os.path.exists(NOTE_DIR):
        print("creating ${NOTE_DIR}")
        os.makedirs(NOTE_DIR)


def open_note(path, at_header=None, append_template=""):
    "open note in editor. creates file on open if not existing"
    if not os.path.isdir(path):
        with open(path, "a+") as f:
            if append_template:
                f.write(append_template)
    if at_header:
        header_found_at = get_line_of_header(path, at_header)
        EDITOR_AT_LINE(header_found_at)
        return
    todays_header, suffix = relative_header(0)
    header_found_at = get_line_of_header(path, todays_header)
    if header_found_at:
        # currently this opens at the line of the header
        # it would be better to open at the bottom of the section containing the header
        EDITOR_AT_LINE(header_found_at)
        return
    else:
        # header not found, append it
        with open(path, "a+") as f:
            f.write("\n\n" + todays_header + suffix + "\n\n")
    EDITOR_AT_LINE(None)


def relative_header(days_ago=0):
    timestamp = time.time() - (3600 * MIDNIGHT_HOUR_SHIFT) - (days_ago * 3600 * 24)
    at_date = datetime.date.fromtimestamp(timestamp)
    return "# " + at_date.strftime(HEADER_STRFTIME), " " + "=" * 20


def get_line_of_header(note_path, header):
    "return line number of header, searching the file from bottom up"
    with open(note_path, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(reversed(lines)):
            if line.startswith(header):
                return len(lines) - i


def get_note_list():
    "return all note filenames [ 1.md, 2.md, ... ]"
    note_list = list(sorted(glob.glob("*.md")))
    return note_list


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
