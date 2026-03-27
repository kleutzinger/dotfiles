#!/usr/bin/env python3
"""
[x] cli
[x] extract image 5 seconds in
[x] display image
[x] get image points
[x] click cli
[] connect image
"""

import random
from vodhelper import extract_vid_frame_to_file, get_vod_duration_ms

# python -m pip install opencv-python
import cv2 as cv
import numpy as np
from typing import List, Tuple

import click

# a list of (x,y) coordinates
PointList = List[Tuple[int, int]]

# add a border of this size around the image for point selection of near or
# beyond the edge of the original image
BORDER_SIZE_PX = 300


def choose_points(path: str, ordered: bool = True) -> PointList:
    """
    make a popup to allow user input of corners of crt. use right click to set 4 points
    points may exist ouside the original image
    """
    filename = path
    img = cv.imread(filename)
    white = [255, 255, 255]
    with_border = cv.copyMakeBorder(
        img,
        BORDER_SIZE_PX,
        BORDER_SIZE_PX,
        BORDER_SIZE_PX,
        BORDER_SIZE_PX,
        cv.BORDER_CONSTANT,
        value=white,
    )
    cv.namedWindow("window", cv.WINDOW_NORMAL)
    cv.imshow("window", with_border)
    # cv.resizeWindow("window", 500, 500)
    pts: list[tuple[int, int]]
    pts = []

    def draw(x):
        if len(pts) < 2:
            return
        d = cv.getTrackbarPos("thickness", "window")
        d = -1 if d == 0 else d
        i = cv.getTrackbarPos("color", "window")
        color = (0, 0, 255)  # red
        with_border[:] = with_border
        cv.polylines(with_border, np.array([pts]), True, color, d)
        cv.imshow("window", with_border)
        # text = f"color={color}, thickness={d}"
        # cv.displayOverlay("window", text)

    def mouse(event, x, y, flags, param):
        if event == cv.EVENT_RBUTTONDOWN:
            pts.append((x, y))
            print(f"point {len(pts)}: ({x}, {y}) (raw with border)")
            draw(0)

    cv.setMouseCallback("window", mouse)
    cv.createTrackbar("color", "window", 0, 6, draw)
    cv.createTrackbar("thickness", "window", 2, 10, draw)
    draw(0)
    while 1:
        k = cv.waitKey(33)
        if k == 27:  # Esc key to stop
            if len(pts) != 4:
                print(f"WARNING: expected 4 points, got {len(pts)}: {pts} — keep clicking")
                continue
            break
    cv.destroyAllWindows()

    def fix_border_coords(pts: PointList) -> PointList:
        out = []
        for x, y in pts:
            out.append((x - BORDER_SIZE_PX, y - BORDER_SIZE_PX))
        return out

    print(f"raw pts (pre-border-fix, {len(pts)} points): {pts}")
    pts = fix_border_coords(pts)
    print(f"pts after border fix: {pts}")
    if ordered:
        ordered_pts = order_pts(pts)
        print(f"pts after ordering: {ordered_pts}")
        return ordered_pts
    return pts


def order_pts(pts: PointList) -> PointList:
    """
    order points to what ffmpeg expects for perspective transforms

    the points are a Z shape
    0........1
    ..........
    ..........
    ..........
    2........3
    i could have used polar coords or something here, but this'll work fine
    """
    print(f"order_pts input ({len(pts)} points): {pts}")
    if len(pts) != 4:
        raise ValueError(f"need 4 points, got {len(pts)}: {pts}")

    cx = sum(p[0] for p in pts) / 4
    cy = sum(p[1] for p in pts) / 4
    print(f"  centroid: ({cx:.1f}, {cy:.1f})")
    for p in pts:
        import math
        angle = math.degrees(math.atan2(p[1] - cy, p[0] - cx))
        quadrant = ("TR" if p[0]>cx else "TL") if p[1]<cy else ("BR" if p[0]>cx else "BL")
        print(f"  {p} angle={angle:.1f}° → {quadrant}")

    sorted_y = sorted(pts, key=lambda p: p[1])
    topleft, topright = sorted(sorted_y[:2], key=lambda p: p[0])
    bottomleft, bottomright = sorted(sorted_y[2:], key=lambda p: p[0])

    print(f"  result: TL={topleft} TR={topright} BL={bottomleft} BR={bottomright}")
    return [topleft, topright, bottomleft, bottomright]


def test_order_pts():
    pts = [(0, 0), (1, 0), (0, 1), (1, 1)]
    assert order_pts(pts) == [(0, 0), (1, 0), (0, 1), (1, 1)]
    assert order_pts(pts[::-1]) == [(0, 0), (1, 0), (0, 1), (1, 1)]


def probe_video(path: str):
    """print rotation metadata and stream dimensions from ffprobe"""
    import subprocess, json
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name:stream_tags=rotate:format_tags=rotate",
        "-of", "json", path,
    ]
    out = subprocess.check_output(cmd).decode()
    info = json.loads(out)
    streams = info.get("streams", [{}])
    s = streams[0] if streams else {}
    tags = s.get("tags", {})
    print(f"[probe] {path}")
    print(f"  stream dims : {s.get('width')}x{s.get('height')}")
    print(f"  rotate tag  : {tags.get('rotate', '(none)')}")
    print(f"  codec       : {s.get('codec_name')}")


def main(num_points: int, path: str, ordered: bool = True) -> PointList:
    print(f"main: {path=}, {num_points=}")
    # check if path is an image
    if path.endswith(".png"):
        return choose_points(path, ordered=ordered)
    probe_video(path)
    frame_second = int(get_vod_duration_ms(path) * random.random() / 1000)
    print(f"extracting frame at {frame_second}s from {path}")
    framepath = extract_vid_frame_to_file(
        path, path + ".png", seek_sec=frame_second, overwrite=True
    )
    print(f"frame extracted to {framepath}")
    ret = choose_points(framepath)
    print(f"choose_points returned: {ret}")
    return ret


def get_perspective_points(path: str) -> PointList:
    pts = main(4, path)
    return order_pts(pts)


# click interface for number of points and path


@click.command()
@click.option("--num_points", default=-1, help="number of points to select")
@click.option("--path", default="test.mp4", help="path to video or png")
@click.option("--ordered", default=False, help="order points for ffmpeg")
def cli(num_points, path, ordered):
    pts = main(num_points, path)
    print(pts)


if __name__ == "__main__":
    cli()
