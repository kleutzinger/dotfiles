#!/usr/bin/env python3
import subprocess
import pygame
import sys
import os

os.environ["SDL_VIDEO_CENTERED"] = "1"  # You have to call this before pygame.init()

# no q
ALPHABET = "WFPARSTZXCVLUYQ;NEIOKM"
SPACING_PX = 200

coord_lookup = dict()


clock = pygame.time.Clock()


def take_scrot() -> None:
    screenshot_path = "/tmp/screenshot.png"
    # take a fullscreen screenshot
    subprocess.run(["scrot", "--overwrite", screenshot_path])
    return screenshot_path


def alph_gen():
    for i in range(len(ALPHABET)):
        for j in range(len(ALPHABET)):
            for k in range(len(ALPHABET)):
                yield ALPHABET[i] + ALPHABET[j] + ALPHABET[k]


# def alph_gen():
#     for i in range(len(ALPHABET)):
#         for j in range(len(ALPHABET)):
#             yield ALPHABET[i] + ALPHABET[j]


if __name__ == "__main__":
    img_path = take_scrot()
    import pygame
    from pygame.locals import *

    pygame.init()
    img = pygame.image.load(img_path)

    white = (255, 64, 64)
    info = (
        pygame.display.Info()
    )  # You have to call this before pygame.display.set_mode()
    screen_width, screen_height = info.current_w, info.current_h
    pygame.font.init()
    screen = pygame.display.set_mode((screen_width, screen_height), FULLSCREEN)
    screen.fill((white))
    running = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        screen.fill((white))
        screen.blit(img, (0, 0))
        # draw red grid on screen
        for i in range(0, screen_width, SPACING_PX):
            pygame.draw.line(screen, (255, 0, 0), (i, 0), (i, screen_height))
            # draw horizontal lines
        for i in range(0, screen_height, SPACING_PX):
            pygame.draw.line(screen, (255, 0, 0), (0, i), (screen_width, i))
        a = alph_gen()
        # put coordinate text in each grid
        for i in range(0, screen_width, SPACING_PX):
            for j in range(0, screen_height, SPACING_PX):
                # map i, j to a unique pair of letters from ALPHABET
                label = next(a)
                text = pygame.font.SysFont("monospace", 40).render(
                    f"{label}", 1, (255, 0, 0)
                )
                coord_lookup[label] = (i, j)
                screen.blit(text, (i + 5, j + 5))

        pygame.display.update()
        clock.tick(60)
