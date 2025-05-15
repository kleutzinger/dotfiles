#!/usr/bin/env -S uv run --script --with pyperclip
"""
Get bracket table from clipboard and convert it to timestamps for youtube description.
"""

import re
import pyperclip
from datetime import timedelta

input_data = pyperclip.paste()


def rm_empty_lines(text):
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def extract_entries(text):
    lines = text.strip().splitlines()
    entries = []

    for i in range(0, len(lines), 2):
        name = lines[i].strip()
        url = lines[i + 1].strip()
        time_match = re.search(r"t=(\d+)", url)
        if time_match:
            seconds = int(time_match.group(1))
            timestamp = str(timedelta(seconds=seconds))
            # ensure HH:MM:SS format
            if len(timestamp.split(":")) == 2:
                timestamp = f"0:{timestamp}"
            timestamp = str(timedelta(seconds=seconds)).rjust(8, "0")
            entries.append((seconds, timestamp, name))

    return sorted(entries)


entries = extract_entries(rm_empty_lines(input_data))

for _, timestamp, name in entries:
    print(f"{timestamp} {name}")
