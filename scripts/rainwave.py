#!/usr/bin/env python3
import os

scripts_dir = os.environ.get("SCRIPTS_DIR") or "/home/kevin/scripts/"
if not os.path.isdir(scripts_dir):
    print(f"no dir at {scripts_dir}, please set $SCRIPTS_DIR")
    exit(1)

stations_glob = os.path.join(scripts_dir, "rainwave-stations", "*")
command = "vlc " + stations_glob
os.system(command)