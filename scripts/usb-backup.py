#!/usr/bin/env python3
"""
run commands to backup directories to drivefrom specified source folders

syncing from multiple machines will merge backups into the smame directory on the drive

That is to say Machine A: ~/Pictures and Mchine B: ~/Pictures will both back up
into External Drive: /Pictures
"""


import os
import subprocess

from common import fzf_choose

SOURCE_DIRS = [
    "~/Pictures",
    "~/Videos",
    "~/Music",
]


def get_source_dirs():
    return [os.path.expanduser(dir) for dir in SOURCE_DIRS]


def run_command(command):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    while True:
        output = process.stdout.readline()
        if output:
            print(output.strip())
        if process.poll() is not None:
            break
    return process.returncode


def select_usb_drive():
    """
    Discover all USB drives mounted under /run/media/<username>/ and select one.
    Returns the full path to the selected drive, e.g.:
    '/run/media/username/drivename'
    """
    base = "/run/media/"
    # Get current username
    username = os.getenv("USER")
    media_path = os.path.join(base, username)

    # Check if media path exists
    if not os.path.exists(media_path):
        print("No USB drives found")
        exit(1)

    # Get all mounted drives
    mounted_drives = []
    for drive in os.listdir(media_path):
        full_path = os.path.join(media_path, drive)
        if os.path.ismount(full_path):
            mounted_drives.append(full_path)

    if len(mounted_drives) == 0:
        print("No USB drives found")
        exit(1)

    if len(mounted_drives) > 1:
        print("Multiple USB drives found")
        return fzf_choose(mounted_drives)
    else:
        return mounted_drives[0]


def backup_dir(source_dir, usb_drive):
    command = f"rsync -avLKW --info=progress2 {source_dir} {usb_drive}"
    run_command(command)


def main():
    usb_drive = select_usb_drive()
    for source_dir in get_source_dirs():
        backup_dir(source_dir, usb_drive)


if __name__ == "__main__":
    main()
