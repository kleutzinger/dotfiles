#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pillow",
# ]
# ///
"""
When collaborating with someone over screenshare, the remote person
may want to "point" somewhere at your screen. We give them a grid
to announce the relevant area coordinate-labeled cells.

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
    scrot: https://github.com/resurrecting-open-source-projects/scrot

#__RUN__# python #__file__#
"""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont


# how many pixels apart should the gridlines be?
# smaller numbers may affect performance
GRID_STEP_SIZE = 100
IS_MAC = os.uname().sysname == "Darwin"

potential_fonts = [
    "/usr/share/fonts/TTF/FiraCode-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
]

for font in potential_fonts:
    if os.path.exists(font):
        FONT_PATH = font
        break
else:
    print("no font found")
    print("tried", potential_fonts)
    exit(1)

if not (os.path.exists(FONT_PATH)):
    print(f"no font found at {FONT_PATH}")
    print("please replace FONT_PATH with a valid font on your machine")
    print('(archlinux) try running "fc-list : file"')
    exit(1)


def grid_on_img(img: Image.Image) -> str:
    "returns path to new img with labeled grid overlaid"
    out_path = "/tmp/screenshot_grid.png"
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, size=20)

    # screen resolution
    W, H = img.size

    # draw grid
    for x in range(0, W, GRID_STEP_SIZE):
        draw.line((x, 0, x, H), fill=128, width=2)
    for y in range(0, H, GRID_STEP_SIZE):
        draw.line((0, y, W, y), fill=128, width=2)

    # draw grid labels
    for y in range(0, H, GRID_STEP_SIZE):
        for x in range(0, W, GRID_STEP_SIZE):
            coord_str = f"{x // GRID_STEP_SIZE},{y // GRID_STEP_SIZE}"
            # Get text size to properly position and create background
            text_width, text_height = draw.textbbox((0, 0), coord_str, font=font)[2:]
            # Center text horizontally within the cell
            text_x = x + (GRID_STEP_SIZE - text_width) // 2
            text_y = y
            # Add dark background behind text with padding
            padding = 2
            draw.rectangle(
                (
                    text_x - padding,
                    text_y - padding,
                    text_x + text_width + padding,
                    text_y + text_height + padding
                ),
                fill=(0, 0, 0, 180)  # Dark semi-transparent background
            )
            draw.text((text_x, text_y), coord_str, font=font, fill=(255, 255, 255))  # White text

    img.save(out_path, "PNG")
    return out_path


def main() -> None:
    screenshot_path = "/tmp/screenshot.png"
    # take a fullscreen screenshot
    # if mac
    if IS_MAC:
        subprocess.run(["screencapture", "-x", screenshot_path])
    else:
        subprocess.run(["scrot", "--overwrite", screenshot_path])
    with Image.open(screenshot_path) as img:
        out_path = grid_on_img(img)
    # display image in fullscreen
    if IS_MAC:
        subprocess.run(["open", "-a", "Preview", out_path])
    else:
        subprocess.run(["feh", "--fullscreen", out_path])


if __name__ == "__main__":
    main()
