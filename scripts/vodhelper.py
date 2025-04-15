#!/usr/bin/python3
"""
#__RUN0__# pushd ~/scripts/vods; vodhelper.py; popd
#__RUN1__# pushd ~/scripts/vods/vods2; vodhelper.py; popd

This is for super smash bros melee replay vod collection to get onto youtube.

see my side streams here:
https://www.youtube.com/watch?v=GE6oQ_OQUjc&list=PL6XKQrv4qTdM8IZMSjCJXn5AXFo601x3J

usage:
    cd <directory of vods (mp4 or ts assumed)>
    # initialize directory
    vodhelper.py

    # once all yamls are populated
    vodhelper.py e

    # TODO:
    # upload to youtube
    vodhelper u


run me in a directory containg vods and i'll help you get them annotated
and perspective corrected

TODOs:
[x] init yamls
    [x] tournament
    [x] each vod
[x] choose perspective for each vod
[x] execute yaml command
    [x] create perspective-corrected vids
    [x] concat all vids into one big 720p video
[x] add text overlay on video
    2022-03-24 Kevbot vs XYZ
[x] automatic adding of youtube description
[] automate youtube upload
    [] generate youtube [x] description [] title
    [] use youtubeuploader script
[]? start.gg api integration
"""

from copy import deepcopy
import datetime
from pprint import pprint

import os
from datetime import date
from subprocess import run
from shlex import split
import subprocess
import sys
import time
from typing import Any, Optional
import re

import yaml

TRNY_YAML_NAME = "tournament.yml"


def convert_bytes(num_bytes: int) -> str:
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return "%3.1f %s" % (num_bytes, x)
        num_bytes /= 1024.0


def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def get_ts_mp4_paths(_dir="./"):
    video_paths = list(
        filter(lambda x: x[-3:] == ".ts" or x[-4:] == ".mp4", os.listdir(_dir))
    )
    video_paths = sorted(video_paths)
    # filter out videos with tmp in their name
    video_paths = list(filter(lambda x: "tmp" not in x, video_paths))
    return list(video_paths)
    # return [os.path.join(_dir, v) for v in video_paths]


def get_vod_duration_ms(vodpath: str) -> float:
    "get length of video in miliseconds"

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        vodpath,
    ]

    ret = subprocess.check_output(cmd)
    # example: b'515.367400\n'
    return int(float(ret.decode().strip()) * 1000)
    # example: 515367


def init_tourney_yaml() -> dict:
    """
    returns path of yaml
    """

    for i in get_ts_mp4_paths():
        if i.count("-") < 1:
            print(
                f"bad video filename, should be in the form VIDEONAME-opponent.mp4: {i}"
            )
            exit(1)
    # VIDEONAME-opponent.mp4
    now = datetime.datetime.today() - datetime.timedelta(hours=20)
    guess_time = now.strftime("%Y-%m-%d")
    nTime = input(
        f"what is the date? \n my guess is\n{guess_time} ({now.strftime('%A')})\ninput something else if not:\n"
    )
    if not nTime:
        nTime = guess_time
    print("assuming trny date today", nTime)
    endpoint = 'https://tril.kevbot.xyz/custom/brackets'
    # fetch endpoint with vanilla python
    import urllib.request
    import json
    req = urllib.request.urlopen(endpoint)
    brackets = json.loads(req.read().decode('utf-8'))
    # brackets is an array of dicts,  find dict with "date" == nTame
    bracket = brackets.find(lambda x: x["date"] == nTime)
    if not bracket:
        print(f"no start.gg url found for {nTime}")
        trny_url = input("start.gg url:")
    else:
        trny_url = bracket["url"]
        print(f"found start.gg url: {trny_url}")
    # get number of vods in directory, aka the number of opponents
    mp4_count = len(get_ts_mp4_paths())
    print(f"found {mp4_count} vods")
    getname = lambda x: os.path.splitext(os.path.basename(x))[0].split("-")[-1]
    opponents = [getname(i) for i in get_ts_mp4_paths()]
    base_yaml = dict(tournament_url=trny_url, date=nTime, opponents=opponents)
    write_yaml(base_yaml, TRNY_YAML_NAME)
    return base_yaml


def get_yaml(y_path: str) -> Any:
    with open(y_path, "r") as f:
        vod = yaml.load(f, Loader=yaml.Loader)
    return vod


def make_or_get_vod_yaml(vidpath: str, tournament: dict, vid_idx: int) -> dict:
    abspath = os.path.abspath(vidpath)
    print(abspath)
    vid_yaml = abspath + ".yml"
    try:
        opponent = tournament["opponents"][vid_idx]
    except IndexError:
        opponent = ""
        pass
    if os.path.exists(vid_yaml):
        return get_yaml(vid_yaml)
    else:
        # file doesn't exist
        vod = dict(
            abspath=abspath,
            path=vidpath,
            ignore=False,
            duration_ms=get_vod_duration_ms(vidpath),
            pers_pts=None,
            frame_pic=None,
            p1="Kevbot (Fox)",
            p2=opponent,
            note="",
            date=tournament["date"],
            start_offset_ms=0,
            end_offset_ms=0,
            filesize=file_size(abspath),
        )
        write_vod_yaml(vod)

    return vod


def write_yaml(obj, path):
    with open(path, "w") as f:
        yaml.dump(obj, f)
    print("wrote obj to", path)


def write_vod_yaml(vod: dict, prev: Optional[dict] = None):
    yaml_path = vod["abspath"] + ".yml"
    print(f"i want to write: {yaml_path=}")
    pprint(vod)
    # if os.path.exists(yaml_path) and prev == get_yaml(yaml_path):
    #     print("no changes, no writing yaml")
    #     return
    input("ctrl + c to cancel?")
    write_yaml(vod, yaml_path)


def gen_perspective_ffmpeg_cmd(
    i_vid_path: str,
    o_vid_path: str,
    ppoints: list[tuple[int, int]],
    preview_only: bool = False,
    text_overlay: str = "",
) -> str:
    """
    ffmpeg can modify perspective of a video file.
    it skews stuff. aka homomorphism
    see https://en.wikipedia.org/wiki/Homomorphism
    or https://news.ycombinator.com/item?id=8713070

    """
    points = ""
    for a, b in ppoints:
        points += f":{a}:{b}"
    # remove first colon
    points = points[1:]
    # check if we're on windows
    if os.name == "nt":
        font_path = "C\\\\:/Windows/Fonts/arial.ttf"
    elif os.name == "posix":
        font_path = "/usr/share/fonts/TTF/Ubuntu Mono Nerd Font Complete Mono.ttf"
    else:
        raise NotImplementedError(f"unknown os {os.name}")
    cmd = (
        f"ffmpeg -y{' -t 3' if preview_only else ''} "
        f"-i '{i_vid_path}' "
        f"-vf "
        f"perspective={points},scale=876:720,setdar=73/60,"
        f"""drawtext=fontfile='{font_path}':text='{text_overlay}':fontcolor=white:fontsize=30:box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=10 """
        "-s 960x720 "
        f"'{o_vid_path}'"
    )

    return cmd


def vod2textoverlay(vod: dict) -> str:
    remove_char_paren = lambda s: (s + " ")[: s.rfind("(")].strip()
    remove_special_chars = lambda s: re.sub(r"[^A-Za-z0-9\- ]+", "", s)
    p1 = remove_char_paren(vod.get("p1", "Kevbot"))
    p2 = remove_char_paren(vod.get("p2", "Opponent"))
    date = vod.get("date", "20XX")
    return remove_special_chars(f"{date} {p1} vs {p2}")


def correctPerspective(vidpath: str, outputpath: str) -> list[tuple[int, int]]:
    """correct perspective of video"""
    from get_img_coords import get_perspective_points

    # y  = rf".\bin\ffmpeg.exe -i .\vid\src-10.mp4 -vf perspective={x},scale=960:720,setdar=4/3 43.mp4"
    points = get_perspective_points(vidpath)

    # ffplay perspective is broken on normal pixel video files, not sure why
    # probably some pixel ratio thing idk
    # cmd = f"ffplay -i {vidpath} -vf perspective={ppoints},scale=960:720,setdar=4/3"

    # workaround is to render a short preview and ask for confirmation on that

    # make preview video
    cmd = gen_perspective_ffmpeg_cmd(
        vidpath,
        outputpath,
        points,
        preview_only=True,
        text_overlay="preview",
    )
    print(cmd)
    # cmd = f"ffmpeg -i {vidpath} -vf perspective={ppoints},scale=960:720,setdar=4u3 out.mp4"

    run(split(cmd))
    run(["mpv", outputpath])
    return points


def extract_vid_frame_to_file(
    input_path: str, output_path: str, seek_sec: int = 0, overwrite: bool = False
) -> str:
    """
    output: a frame as a jpg
    """
    ibasename, iext = os.path.splitext(input_path)
    obasename, oext = os.path.splitext(output_path)
    if oext not in [".png", ".jpg"]:
        # ensure output is an image
        # lets go with .jpg
        output_path = output_path + ".png"

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{seek_sec}",
        "-i",
        f"{input_path}",
        "-frames:v",
        "1",
        "-q:v",
        "2",
        f"{output_path}",
    ]
    if overwrite:
        cmd = cmd[0:1] + ["-y"] + cmd[1:]
    subprocess.run(cmd)
    return output_path


def execute_ymls(yaml_paths: list[str], preview_only=False):
    """
    now that we have all the yaymls written, actually render the final videos
    [x] render individual perspective-corrected vids
    [x] concat them together into 720p vid
        melt worked well for this
    [x] add text overlay to indicate players?
    """
    os.makedirs("corrected", exist_ok=True)
    vids_txt = "vids.txt"
    with open(vids_txt, "w") as f:
        # empty the vids.txt file
        f.write("")
    for idx, y in enumerate(sorted(yaml_paths)):
        vod = get_yaml(y)
        # make perspective videos work
        outname = f"{idx:03}" + vod["path"]
        vod["output_path"] = os.path.join("corrected", outname)
        ffmpeg_cmd = gen_perspective_ffmpeg_cmd(
            i_vid_path=vod["path"],
            o_vid_path=vod["output_path"],
            ppoints=vod["pers_pts"],
            preview_only=preview_only,
            text_overlay=vod2textoverlay(vod),
        )
        print(ffmpeg_cmd)
        run(split(ffmpeg_cmd))
        with open(vids_txt, "a") as f:
            f.write(f"file {vod['output_path']}\n")


def get_desc(trny: dict, vods: list[dict], pic_offset: int = 5) -> tuple[str, str]:
    "return title of video, description for youtube"

    desc = ""
    desc += trny["date"] + "\n"
    desc += trny["tournament_url"] + "\n"

    cur_sec = 0
    sec2ts = lambda s: str(datetime.timedelta(seconds=s))
    for vod in vods:
        desc += f"{sec2ts(cur_sec)} "
        desc += f"{vod['p1']} vs {vod['p2']}\n"
        cur_sec += round(vod["duration_ms"] / 1000)
        cur_sec += pic_offset
    print(desc)
    return "title", desc


def main():
    if "e" in sys.argv:
        # execute populated yamls and kick off rendering
        ymls = [i for i in os.listdir() if i.endswith(".yml") and i != TRNY_YAML_NAME]
        input(
            f'start render? (will overwrite stuff in "./corrected").\n{len(ymls)} ymls files found'
        )
        if TRNY_YAML_NAME in ymls:
            ymls.remove(TRNY_YAML_NAME)
        execute_ymls(ymls, preview_only="s" in sys.argv)
        trny = get_yaml(TRNY_YAML_NAME)
        vods = [get_yaml(i) for i in sorted(os.listdir()) if i.endswith("mp4.yml")]
        desc = get_desc(trny, vods)
        with open("description-5-offset.txt", "w") as f:
            f.write(desc[1])
        desc = get_desc(trny, vods, pic_offset=0)
        with open("description-no-offset.txt", "w") as f:
            f.write(desc[1])
        exit(0)

    # preprocess videos, add metadata. Idempotent probably.
    if not os.path.exists(TRNY_YAML_NAME):
        print(f"no {TRNY_YAML_NAME} found, creating")
        init_tourney_yaml()
    tournament = get_yaml(TRNY_YAML_NAME)
    vid_paths = get_ts_mp4_paths()
    os.makedirs("tmp", exist_ok=True)
    print(len(vid_paths), len(tournament["opponents"]))
    for vid_idx, vid_path in enumerate(vid_paths):
        vod = make_or_get_vod_yaml(vid_path, tournament, vid_idx)
        prev_vod = deepcopy(vod)
        print(f"{vid_path=}")
        if vod.get("pers_pts") is None:
            while True:
                points = correctPerspective(vid_path, os.path.join("tmp", "out.mp4"))
                if len(points) != 4:
                    print(f"bad {len(points)=}. should be 4")
                    continue
                inp = input("r to retry, y to continue").lower()
                if "r" in inp:
                    continue
                else:
                    break

            vod["pers_pts"] = points
        if vod.get("p2") is None:
            vod["p2"] = input("player 2?: ")
        print(vod2textoverlay(vod))
        write_vod_yaml(vod, prev=prev_vod)


if __name__ == "__main__":
    main()
