#!/usr/bin/env python3

import subprocess
import json
import urllib.parse


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
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Error: {}".format(result.stderr))
    selected_image_url = result.stdout.strip()
    selected_coconut = None
    selected_index = None
    for i, c in enumerate(coconuts):
        if c["imageUrl"] == selected_image_url:
            selected_coconut = c
            selected_index = i
            break
    if not selected_coconut or selected_index is None:
        raise Exception(
            "Error: No coconut found for image URL {}".format(selected_image_url)
        )
    rotated_coconuts = coconuts[selected_index:] + coconuts[:selected_index]
    """
    #EXTM3U
    #EXTVLCOPT:start-time=sec
    ./videopath
    #EXTVLCOPT:start-time=sec
    ./videopath
    """
    with open("/tmp/coconuts.m3u8", "w") as f:
        f.write("#EXTM3U\n")
        for c in rotated_coconuts:
            encoded_path = urllib.parse.quote(c["path"])
            sec = c["sec"]
            f.write(f"#EXTVLCOPT:start-time={sec}\n")
            f.write(f"{encoded_path}\n")
    cmd = ["vlc", "--no-video-title-show", "--loop", "/tmp/coconuts.m3u8"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
