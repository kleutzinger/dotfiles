#!/usr/bin/env python3

import subprocess
import os
import json
from pprint import pprint


def get_coconut_list():
    cmd = ["coconut.js", "--list"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise Exception("Error: {}".format(err))
    out_str = out.decode("utf-8", errors="ignore")
    return json.loads(out_str)


def filter_coconut(coconuts):
    return [c for c in coconuts if c.get("exists")]


if __name__ == "__main__":
    coconuts = get_coconut_list()[::-1]
    coconuts = filter_coconut(coconuts)  # rm non-existent coconuts
    imageUrls = [c["imageUrl"] for c in coconuts]
    cmd = ["image_selector2.py"] + imageUrls
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise Exception("Error: {}".format(err))
    selected_image_url = out.decode("utf-8").strip()
    selected_coconut = [c for c in coconuts if c["imageUrl"] == selected_image_url][0]
    sec = selected_coconut["sec"]
    cmd = ["vlc", selected_coconut["path"], "--start-time", str(sec)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
