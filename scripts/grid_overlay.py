#!/usr/bin/env python3
"""
When collaborating with someone over screenshare, the person on the other end
may want to "point" somewhere at your screen.

This script:
1. takes a screenshot of your screen
2. modifies the image:
    2a. adds a grid over the image
    2b. adds a coordinate label in each cell
3. displays the new image in fullscreen

The other person can now announce the relevant coordinate
You press q to quit and continue collaborating.


This script should be bound to a hotkey
Mine is super + shift + h

must have these pre-installed
    PIL: https://pillow.readthedocs.io/en/stable/index.html
    feh: https://feh.finalrewind.org/
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/TTF/FiraCode-Bold.ttf"

if not (os.path.exists(FONT_PATH)):
    print(f"no font found at {FONT_PATH}")
    print("please replace FONT_PATH with a valid font on your machine")
    print('(archlinux) try running "fc-list : file"')
    exit(1)


def grid_on_img(img: Image.Image) -> str:
    "returns path to new img with labeled grid overlaid"
    out_path = "/tmp/screenshot_grid.png"
    draw = ImageDraw.Draw(img)
    # how many pixels apart should the gridlines be?
    # smaller numbers affect performance
    step_size = 100
    font = ImageFont.truetype(FONT_PATH, size=20)

    # screen resolution
    W, H = img.size

    # draw grid
    for x in range(0, W, step_size):
        draw.line((x, 0, x, H), fill=128)
    for y in range(0, H, step_size):
        draw.line((0, y, W, y), fill=128, width=4)

    # draw grid labels
    for y in range(0, H, step_size):
        for x in range(0, W, step_size):
            coord_str = f"{x//step_size},{y//step_size}"
            ts = font.getsize(coord_str)
            draw.rectangle((x, y, x + ts[0], y + ts[1]), fill=128)
            draw.text((x, y), coord_str, font=font)

    img.save(out_path, "PNG")
    return out_path


def main() -> None:
    screenshot_path = "/tmp/screenshot.png"
    # take a fullscreen screenshot
    subprocess.run(["scrot", "--overwrite", screenshot_path])
    with Image.open(screenshot_path) as img:
        out_path = grid_on_img(img)
    # dispaly image in fullscreen
    subprocess.run(["feh", "--fullscreen", out_path])


if __name__ == "__main__":
    main()
