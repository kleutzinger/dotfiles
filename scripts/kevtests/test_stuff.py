#!/usr/bin/env python3
"""
this file tests that my computer is in a good state
"""

import os
import psutil
from subprocess import check_output


def test_disk_space_not_nearly_full():
    free_space = psutil.disk_usage(".")
    error_msg = f"Disk space is nearly full: {free_space.percent}%"
    assert free_space.percent < 85, error_msg


def test_no_temp_files_in_home_directory():
    disallowed_substrings = {"tmp", "temp", "test"}
    found = []
    for filename in os.listdir(os.path.expanduser("~")):
        for substring in disallowed_substrings:
            if filename == "Templates":
                continue
            if substring in filename.lower():
                found.append(filename)
    assert not found, f"Temporary files found"


def test_yadm_up_to_date():
    # yadm status is like git status
    status = check_output(["yadm", "status"]).decode()
    # check no changes to tracked files
    assert "nothing to commit" in status
