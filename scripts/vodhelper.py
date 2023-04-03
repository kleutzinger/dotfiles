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
[] automatic adding of youtube description
[] automate youtube upload
    [] generate youtube [x] description [] title
    [] use youtubeuploader script
[]? start.gg api integration
"""

from copy import deepcopy
import datetime
from pprint import pprint
import shutil

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


def replaceExtension(filename, new_ext) -> str:
    basename, _ = os.path.splitext(filename)
    return basename + new_ext


def convert_bytes(num_bytes: int) -> str:
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return "%3.1f %s" % (num_bytes, x)
        num_bytes /= 1024.0


def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def get_ts_files(_dir="./"):
    ts_files = list(filter(lambda x: x[-3:] == ".ts", os.listdir(_dir)))
    ts_files = sorted(ts_files)
    return ts_files


def get_ts_paths(_dir="./"):
    ts_files = list(filter(lambda x: x[-3:] == ".ts", os.listdir(_dir)))
    ts_files = sorted(ts_files)
    return [os.path.join(_dir, t) for t in ts_files]


def get_ts_mp4_paths(_dir="./"):
    video_paths = list(
        filter(lambda x: x[-3:] == ".ts" or x[-4:] == ".mp4", os.listdir(_dir))
    )
    video_paths = sorted(video_paths)
    return list(video_paths)
    # return [os.path.join(_dir, v) for v in video_paths]


def promptTsFiles(ts_paths):
    skipConversion = False
    for idx, ts_path in enumerate(ts_paths):
        if skipConversion:
            break
        ts = os.path.basename(ts_path)
        # print(ts_path)
        size = file_size(ts_path)
        while not skipConversion:
            prompt = f"#{idx+1}/{len(ts_paths)}\n"
            prompt += f"{ts} \nsize: {size}\n"
            prompt += (
                "cmds:(v)preview (r)ename (n)ext (d)elete (l)ist (s)kipConversion: "
            )
            print("\n\n\n")
            cmd = input(prompt)
            if cmd == "v":  # view preview in vlc
                subprocess.call(f'/usr/bin/mplayer "{ts_path}"', shell=True)
            elif cmd == "r":  # rename
                no_extension, ext = os.path.splitext(ts)
                append_to_filename = input(f"rename to: {no_extension}")
                new_filename = no_extension + append_to_filename + ext
                os.rename(ts_path, new_filename)
                print("renamed: ", new_filename)
                ts = new_filename
                ts_path = os.path.abspath(ts)
            elif cmd == "d":  # move to delete folder
                os.makedirs("del", exist_ok=True)
                source = ts_path
                destination = os.path.join(os.path.curdir, "del", ts)
                os.rename(source, destination)
                break
            elif cmd == "n":  # continue to next file
                break
            elif cmd == "l":
                print("\n".join(get_ts_files()))
            elif cmd == "s":
                skipConversion = True
            else:
                continue
    return get_ts_paths()


def addBrackets(str_):
    return f"({str_})"
    # return '[' + _str + ']'


def generateTitleString(ts_basename, tournament_name=""):
    try:
        leading_nums = ts_basename[:15]
        year = leading_nums[:4]
        month = leading_nums[4:6]
        num2month = {
            "01": "Jan",
            "02": "Feb",
            "03": "Mar",
            "04": "Apr",
            "05": "May",
            "06": "Jun",
            "07": "Jul",
            "08": "Aug",
            "09": "Sept",
            "10": "Oct",
            "11": "Nov",
            "12": "Dec",
        }
        month = num2month[month]
        day = leading_nums[6:8]
        date_str = " ".join([year, month, day])
        # if len(ts_basename) > 18:  # filename has added title
        # date_str = ' ' + date_str
        date_str = addBrackets(date_str)
        filename, ext = os.path.splitext(ts_basename)
        # if len(batch_idx) > 0:
        #     batch_idx = addBrackets(batch_idx)
        if len(tournament_name) > 0:
            tournament_name = addBrackets(tournament_name)
        return f"{filename[15:]} {date_str} {tournament_name}{ext}"
    except Exception as e:
        print(e)
        return ts_basename


# if input('do not copy+convert? x to cancel: ') != 'x':


def copyTS(ts_paths=get_ts_paths()):
    now = datetime.datetime.today() - datetime.timedelta(hours=20)
    nTime = now.strftime("%Y-%m-%d-%f")
    customFolderName = input("output folder name?: ")
    outputFolder = f'/home/kevin/output/{" ".join([nTime, customFolderName])}'
    os.makedirs(outputFolder, exist_ok=True)
    print(nTime)
    for ts_path in ts_paths:
        source = ts_path
        destination = outputFolder
        shutil.copy(source, destination)
        print("done copying ", ts_path)
    return outputFolder
    # goto new folder and covnert c


def convert(
    ts_paths=get_ts_paths(), append_to_filename=""
):  # makes file.mp4 in mp4 folder
    outputMP4s = []
    for idx, ts_path in enumerate(ts_paths):
        ts_dirname = os.path.dirname(ts_path)
        os.makedirs(os.path.join(ts_dirname, "mp4"), exist_ok=True)
        # idx_no = str(idx+1).zfill(2)
        basename = os.path.basename(ts_path)
        # mp4name = generateTitleString(
        #     basename, f'{idx_no}_{len(ts_paths)}')
        mp4name = generateTitleString(basename, append_to_filename)

        mp4name = replaceExtension(mp4name, ".mp4")
        # figure out why not mp4 folder?
        outputPath = os.path.join(ts_dirname, "mp4", mp4name)
        outputMP4s.append(outputPath)
        subprocess.call(
            f'ffmpeg -y -i "{ts_path}" -preset veryfast -vf scale=1280:-2 "{outputPath}"',
            shell=True,
        )
    return outputMP4s


def uploadFolder(_dir="./", desc="", vis=""):
    video_paths = get_ts_mp4_paths(_dir)
    for v in video_paths:
        uploadVideo(v, desc=desc, vis=vis)


example_ts_path = "/home/kevin/test/202001251759330.ts"


# print(generateTitleString(os.path.basename(example_ts_path)))


def uploadVideo(videoPath, title="", desc="", vis=""):
    if vis == "p":
        vis = "public"
    else:
        vis = "unlisted"
    if len(title) == 0:
        title = os.path.splitext(os.path.basename(videoPath))[0]
    uploadCmd = f'~/scripts/youtubeuploader -oe -op "{vis}" -od "{desc}" -ot "{title}" -l -v "{videoPath}"'
    subprocess.call(uploadCmd, shell=True)


def getGlobalFlags():
    pass


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


def init_tourney_yaml() -> str:
    """
    returns path of yaml
    """
    today = str(date.today())
    print("assuming trny date today", today)
    trny_url = input("start.gg url:")
    opponents = input("comma separated opponents:").split(",")
    base_yaml = dict(tournament_url=trny_url, date=today, opponents=opponents)
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
    if "y" not in input("y to write").lower():
        print("not writing")
        return
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
    cmd = (
        f"ffmpeg -y{' -t 3' if preview_only else ''} "
        f"-i {i_vid_path} "
        f"-vf "
        f"perspective={points},scale=960:720,setdar=4/3,"
        f"""drawtext=fontfile='/usr/share/fonts/TTF/Ubuntu Mono Nerd Font Complete Mono.ttf':text='{text_overlay}':fontcolor=white:fontsize=30:box=1:boxcolor=black@0.5:boxborderw=5:x=10:y=10 """
        "-s 960x720 "
        f"{o_vid_path}"
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
    os.makedirs("final", exist_ok=True)
    final_output_path = os.path.join("final", f"final_{time.time()}.mp4")
    # cmd = f"ffmpeg -f concat -safe 0 -i {vids_txt} {final_output_path}"
    mp4list = " ".join(
        sorted(
            [
                os.path.join("corrected", i)
                for i in os.listdir("corrected")
                if i.endswith("mp4")
            ]
        )
    )
    cmd = f"melt {mp4list} -consumer avformat:{final_output_path}"
    print(cmd)
    run(split(cmd))
    run(["mpv", final_output_path])


def get_desc(trny: dict, vods: list[dict]) -> tuple[str, str]:
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
    print(desc)
    return "title", desc


def main():

    if "d" in sys.argv:
        trny = get_yaml(TRNY_YAML_NAME)
        vods = [get_yaml(i) for i in sorted(os.listdir()) if i.endswith("mp4.yml")]
        get_desc(trny, vods)
        exit()

    if "e" in sys.argv:
        input('start render? (will overwrite stuff in "corrected" and "final)')
        ymls = [i for i in os.listdir() if i.endswith(".yml")]
        if TRNY_YAML_NAME in ymls:
            ymls.remove(TRNY_YAML_NAME)
        execute_ymls(ymls, preview_only="s" in sys.argv)

    if not os.path.exists(TRNY_YAML_NAME):
        print(f"no {TRNY_YAML_NAME} found, creating")
        init_tourney_yaml()
    tournament = get_yaml(TRNY_YAML_NAME)
    vid_paths = get_ts_mp4_paths()
    os.makedirs("tmp", exist_ok=True)
    assert len(vid_paths) == len(tournament["opponents"])
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
                if "r" not in input("r to retry").lower():
                    break
            vod["pers_pts"] = points
        if vod.get("p2") is None:
            vod["p2"] = input("player 2?: ")
        print(vod2textoverlay(vod))
        write_vod_yaml(vod, prev=prev_vod)

    # init_yaml(vid_paths)
    # ts_paths = get_ts_files()  # current folder ts paths
    # renamed_ts_paths = promptTsFiles(ts_paths)
    # copied_output_folder = copyTS(renamed_ts_paths)
    # output_mp4_paths = convert(
    #     get_ts_paths(copied_output_folder), flags["tournament_name"]
    # )
    # subprocess.call(
    #     f'notify-send -u critical "conversion complete {copied_output_folder}/mp4"',
    #     shell=True,
    # )

    # Disable uploads (api rate-limited too heavily)
    """
    for mp4_path in output_mp4_paths:
        uploadVideo(
            mp4_path, desc=flags['bracketURL'], vis=flags['visibility'])
    """


if __name__ == "__main__":
    main()
