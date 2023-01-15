#!/usr/bin/env python3
"""
[x] cli
[x] extract image 5 seconds in
[x] display image
[x] get image points
[] connect image
"""

from vodhelper import extract_vid_frame_to_file, get_vod_duration_ms
import cv2 as cv
import numpy as np
from typing import List, Tuple

PointList = List[Tuple[int, int]]

# print(dir(cv2))


def choose_points(path: str) -> PointList:
    """
    make a popup to allow user input of corners of crt. use right click to set 4 points
    """
    filename = path
    print(path)
    img = cv.imread(filename)
    cv.imshow("window", img)
    pts: list[tuple[int, int]]
    pts = []

    def draw(x):
        d = cv.getTrackbarPos("thickness", "window")
        d = -1 if d == 0 else d
        i = cv.getTrackbarPos("color", "window")
        color = (0, 0, 255)  # red
        img[:] = img
        cv.polylines(img, np.array([pts]), True, color, d)
        cv.imshow("window", img)
        text = f"color={color}, thickness={d}"
        cv.displayOverlay("window", text)

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
    return order_pts(pts)


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

    topleft = list(top2.intersection(left2))[0]
    topright = list(top2.intersection(right2))[0]
    bottomleft = list(bottom2.intersection(left2))[0]
    bottomright = list(bottom2.intersection(right2))[0]

    return [topleft, topright, bottomleft, bottomright]


def test_order_pts():
    pts = [(0, 0), (1, 0), (0, 1), (1, 1)]
    assert order_pts(pts) == [(0, 0), (1, 0), (0, 1), (1, 1)]
    assert order_pts(pts[::-1]) == [(0, 0), (1, 0), (0, 1), (1, 1)]


def main(num_points: int, path: str) -> PointList:
    center_second = get_vod_duration_ms(path) / 2 // 1000
    framepath = extract_vid_frame_to_file(
        path, path + ".png", seek_sec=center_second, overwrite=True
    )
    ret = choose_points(framepath)
    return ret


def get_perspective_points(path: str) -> PointList:
    pts = main(4, path)
    return order_pts(pts)


if __name__ == "__main__":
    main()
