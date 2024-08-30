#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
import shutil
from pprint import pprint

import click

"""
gets files and puts them into the equivalent location in the receiver's home

two commands:
1. sendfiles.py send <file0> <file1> ... <fileN>
2. sendfiles.py rec <code>
use croc
"""

MANIFEST_NAME = "manifest-sendfile.json"


@click.command()
@click.argument("files", nargs=-1)
def send(files):
    """
    send files using croc
    make a manifest, too
    """
    files = list(files)
    manifest = {
        "homedir": os.path.expanduser("~"),
        "files": [
            {
                "name": os.path.basename(f),
                "size": os.path.getsize(f),
                "abspath": os.path.abspath(f),
            }
            for f in files
        ],
    }
    if len(files) == 0:
        print("No files to send")
        return
    with open(MANIFEST_NAME, "w") as f:
        json.dump(manifest, f, indent=4)
    print(json.dumps(manifest, indent=4))
    files += [MANIFEST_NAME]
    print("Sending files: ", files)
    files += [MANIFEST_NAME]
    cmd = ["croc", "send"] + files
    print(cmd)
    subprocess.run(cmd)
    # clean up manifest file
    os.remove(MANIFEST_NAME)


@click.command()
@click.argument("code")
def rec(code):
    # cd to temp dir
    tempdir = tempfile.mkdtemp()
    os.chdir(tempdir)
    click.echo("Receiving files in: " + tempdir)
    print("Receiving files with code: ", code)
    cmd = ["croc", code]
    subprocess.run(cmd)
    # read manifest
    with open(MANIFEST_NAME) as f:
        manifest = json.load(f)
    # move files to my own equivalent paths in my home
    copies = []
    for file in manifest["files"]:
        their_homedir = manifest["homedir"]
        their_abspath = file["abspath"]
        # put the file in the equivalent path in my home
        my_homedir = os.path.expanduser("~")
        my_abspath = their_abspath.replace(their_homedir, my_homedir)
        if os.path.exists(my_abspath):
            print("File exists, still sending", my_abspath)
        # make sure the directory exists
        os.makedirs(os.path.dirname(my_abspath), exist_ok=True)
        # copy the file
        copies.append((file, my_abspath))
    print(json.dumps([path for _, path in copies], indent=4))
    input("Press enter to write above files")
    for file, my_abspath in copies:
        shutil.copy(file["name"], my_abspath)
        print("Copied: ", file["name"], " to ", my_abspath)
    # remove tempdir
    input(f"Press enter to remove tempdir {tempdir}")
    shutil.rmtree(tempdir)
    print(f"Removed tempdir: {tempdir}")
    print("done")


@click.group()
def cli():
    pass


cli.add_command(send)
cli.add_command(rec)
cli.add_command(rec, name="croc")

# main func
if __name__ == "__main__":
    cli()
