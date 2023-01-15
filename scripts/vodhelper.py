#!/usr/bin/python3
"""
#__RUN0__# pushd ~/scripts/vods; vodhelper.py; popd
#__RUN1__# pushd ~/scripts/vods/vods2; vodhelper.py; popd

This is for super smash bros melee replay vod collection. see



usage:
    cd <directory of vods (mp4 or ts assumed)>
    vodhelper.py

run me in a directory containg vods and i'll help you get them annotated
and perspective corrected

TODOs:
[x] init yamls
    [x] tournament
    [x] each vod
[x] choose perspective for each vod
[] execute yaml command
    [] create perspective-corrected vids
    [] concat all vids into one big 720p video
[] automate youtube upload
    [] generate youtube description
    [] use youtubeuploader script
"""

from copy import deepcopy
from pprint import pprint
import shutil

import os
from datetime import date
from subprocess import run
from shlex import split
import subprocess
from typing import Any, Optional

import yaml

TRNY_YAML_NAME = "tournament.yml"


def replaceExtension(filename, new_ext):
    basename, _ = os.path.splitext(filename)
    return basename + new_ext


def convert_bytes(num):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


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
    now = datetime.datetime.today()
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


print(generateTitleString(os.path.basename(example_ts_path)))


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


def init_tourney_yaml() -> None:
    today = str(date.today())
    print("assuming trny date today", today)
    trny_url = input("start.gg url:")
    base_yaml = dict(tournament_url=trny_url, date=today)
    write_yaml(base_yaml, TRNY_YAML_NAME)


def get_yaml(y_path: str) -> Any:
    with open(y_path, "r") as f:
        vod = yaml.load(f, Loader=yaml.Loader)
    return vod


def make_or_get_vod_yaml(vidpath: str) -> dict:
    abspath = os.path.abspath(vidpath)
    print(abspath)
    vid_yaml = abspath + ".yml"
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
            p2=None,
            note="",
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
    write_yaml()


def correctPerspective(vidpath: str, outputpath: str) -> list[tuple[int, int]]:
    """correct perspective of video"""
    from get_img_coords import get_perspective_points

    # y  = rf".\bin\ffmpeg.exe -i .\vid\src-10.mp4 -vf perspective={x},scale=960:720,setdar=4/3 43.mp4"
    points = get_perspective_points(vidpath)
    ppoints = ""
    for a, b in points:
        ppoints += f":{a}:{b}"
    # remove first colon
    ppoints = ppoints[1:]

    # ffplay perspective is broken on normal pixel video files, not sure why
    # probably some pixel ratio thing idk
    # cmd = f"ffplay -i {vidpath} -vf perspective={ppoints},scale=960:720,setdar=4/3"

    # workaround is to render a short preview and ask for confirmation on that
    def gen_cmd(preview_only: bool = False) -> str:
        cmd = (
            f"ffmpeg{' -y -t 3' if preview_only else ''} "
            f"-i {vidpath} -vf perspective={ppoints},scale=960:720,setdar=4/3 {outputpath}"
        )
        return cmd

    cmd = gen_cmd(preview_only=True)
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


def execute_ymls():
    raise NotImplementedError


def main():
    if not os.path.exists(TRNY_YAML_NAME):
        print(f"no {TRNY_YAML_NAME} found, creating")
        init_tourney_yaml()
    vid_paths = get_ts_mp4_paths()
    os.makedirs("tmp", exist_ok=True)
    for vid_path in vid_paths:
        vod = make_or_get_vod_yaml(vid_path)
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
