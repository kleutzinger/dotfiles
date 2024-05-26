#!/usr/bin/env python3
"""
this file tests that my computer is in a good state
"""

import os
import psutil
import urllib.request
from subprocess import check_output, run
import shutil


def test_disk_space_not_nearly_full():
    free_space = psutil.disk_usage(".")
    error_msg = f"Disk space is nearly full: {free_space.percent}%"
    assert free_space.percent < 85, error_msg


def test_no_temp_files_in_home_directory():
    """
    I don't like having temporary files in my home directory
    """
    disallowed_substrings = {"tmp", "temp", "out", "test"}
    img_extensions = {"jpg", "jpeg", "png", "gif", "svg", "bmp", "tiff"}
    vid_extensions = {"mp4", "mkv", "avi", "mov", "flv", "wmv", "webm"}
    txt_extensions = {"txt", "md", "rst", "tex", "pdf"}
    archive_extensions = {"zip", "tar", "gz", "xz", "bz2", "7z", "rar", "tgz"}
    disallowed_file_extensions = archive_extensions | img_extensions | txt_extensions | vid_extensions
    allowed_filenames = {"Templates", ".bash_logout", "README.md", ".textsnatcher.txt"}
    found = []
    for filename in os.listdir(os.path.expanduser("~")):
        if filename in allowed_filenames:
            continue
        for substring in disallowed_substrings:
            if substring in filename.lower():
                found.append(filename)
                continue
        for extension in disallowed_file_extensions:
            if filename.endswith(extension):
                found.append(filename)
    found = list(set(found))
    assert not found, f"Temporary files found"


def test_local_yadm_clean():
    # yadm status is like git status
    status = check_output(["yadm", "status", "-s"]).decode()
    # check no changes to tracked files nor remote changes
    assert not status, f"local changes detected by yadm:\n{status}"


def test_remote_yadm_up_to_date():
    run(["yadm", "fetch"])
    status = check_output(["yadm", "status"]).decode()
    # check no changes upstream remote
    assert (
        "Your branch is up to date" in status
    ), f"remote changes detected by yadm:\n{status}"


def test_no_missing_arch_packages():
    """
    not covered edge case: package names that are a substring of another package name
    """
    if not shutil.which("yay"):
        print("yay not installed, skipping test")
        return
    desired_packages = os.path.expanduser("~/.config/yadm/arch_packages.txt")
    with open(desired_packages) as f:
        desired_packages = set(f.read().splitlines())
        installed_packages = check_output(["yay", "-Q"]).decode()
        not_installed = []
        for package in desired_packages:
            if package not in installed_packages:
                not_installed.append(package)
        correction_command = "yay -S " + " ".join(not_installed)
        print(correction_command)
        assert not not_installed, f"Missing Packages:\n{correction_command}"


def test_kevbot_xyz_reachable():
    """
    check that kevbot.xyz is reachable
    this makes sure that my internet connection is working
    """
    resp = urllib.request.urlopen("https://kevbot.xyz", timeout=5)
    assert resp.code == 200, f"kevbot.xyz is unreachable"


def test_swapfile_active():
    """
    check that a swapfile is active
    """
    swapfile = check_output(["swapon", "--show"]).decode()
    swapfile = swapfile.splitlines()[1]
    swapfile = swapfile.split()
    assert swapfile[0] == "/swapfile", f"swapfile not active: {swapfile}"


def test_homedir_is_called_kevin():
    """
    check that my home directory is called kevin
    """
    assert os.path.expanduser("~") == "/home/kevin", "home directory is not /home/kevin"


def test_local_bin_dir_exists():
    """
    check that my local bin directory exists
    """
    assert os.path.isdir(os.path.expanduser("~/.local/bin")), "~/.local/bin directory does not exist"


def test_no_pacman_lockfile():
    """
    check that there is no pacman lockfile
    """
    assert not os.path.isfile("/var/lib/pacman/db.lck"), "pacman lockfile exists"
