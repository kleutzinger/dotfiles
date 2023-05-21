#!/usr/bin/env python3
"""
[x] cli
[x] extract image 5 seconds in
[x] display image
[x] get image points
[] connect image
"""

import random
from vodhelper import extract_vid_frame_to_file, get_vod_duration_ms
import cv2 as cv
import numpy as np
from typing import List, Tuple

# a list of (x,y) coordinates
PointList = List[Tuple[int, int]]

# add a border of this size around the image for point selection of near or
# beyond the edge of the original image
BORDER_SIZE_PX = 300

# print(dir(cv2))


def choose_points(path: str) -> PointList:
    """
    make a popup to allow user input of corners of crt. use right click to set 4 points
    points may exist ouside the original image
    """
    filename = path
    print(path)
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
    cv.imshow("window", with_border)
    pts: list[tuple[int, int]]
    pts = []

    def draw(x):
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
            draw(0)

    cv.setMouseCallback("window", mouse)
    cv.createTrackbar("color", "window", 0, 6, draw)
    cv.createTrackbar("thickness", "window", 2, 10, draw)
    draw(0)
    while 1:
        k = cv.waitKey(33)
        if k == 27:  # Esc key to stop
            break
    cv.destroyAllWindows()

    def fix_border_coords(pts: PointList) -> PointList:
        out = []
        for x, y in pts:
            out.append((x - BORDER_SIZE_PX, y - BORDER_SIZE_PX))
        return out

    return order_pts(fix_border_coords(pts))


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
    # assert len(pts) == 4
    if len(pts) != 4:
        print("bad len of pts")
        return []

    left2 = set(sorted(pts, key=lambda p: p[0])[:2])
    right2 = set(sorted(pts, key=lambda p: p[0])[2:])

    top2 = set(sorted(pts, key=lambda p: p[1])[:2])
    bottom2 = set(sorted(pts, key=lambda p: p[1])[2:])

    topleft = top2.intersection(left2).pop()
    topright = top2.intersection(right2).pop()
    bottomleft = bottom2.intersection(left2).pop()
    bottomright = bottom2.intersection(right2).pop()

    return [topleft, topright, bottomleft, bottomright]


def test_order_pts():
    pts = [(0, 0), (1, 0), (0, 1), (1, 1)]
    assert order_pts(pts) == [(0, 0), (1, 0), (0, 1), (1, 1)]
    assert order_pts(pts[::-1]) == [(0, 0), (1, 0), (0, 1), (1, 1)]


def main(num_points: int, path: str) -> PointList:
    frame_second = int(get_vod_duration_ms(path) * random.random() / 1000)
    frame_second = 0
    framepath = extract_vid_frame_to_file(
        path, path + ".png", seek_sec=frame_second, overwrite=True
    )
    ret = choose_points(framepath)
    return ret


def get_perspective_points(path: str) -> PointList:
    pts = main(4, path)
    return order_pts(pts)


# if __name__ == "__main__":
#     main()
