#!/usr/bin/env python3
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys

# Initialize Pygame
pygame.init()

# Set display dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DISPLAY_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Set colors
WHITE = (255, 255, 255)

# Set image parameters
IMAGE_SIZE = 200
GAP = 20
MAX_IMAGES_PER_ROW = (SCREEN_WIDTH - GAP) // (IMAGE_SIZE + GAP)


# Function to load images
def load_images(image_paths):
    images = []
    for path in image_paths:
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (IMAGE_SIZE, IMAGE_SIZE))
        images.append(image)
    return images


# Function to display images in a gallery
def display_gallery(screen, images, image_paths):
    num_images = len(images)
    rows = (num_images - 1) // MAX_IMAGES_PER_ROW + 1

    running = True

    while running:
        screen.fill(WHITE)

        for i in range(num_images):
            x = (i % MAX_IMAGES_PER_ROW) * (IMAGE_SIZE + GAP) + GAP
            y = (i // MAX_IMAGES_PER_ROW) * (IMAGE_SIZE + GAP) + GAP
            screen.blit(images[i], (x, y))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                clicked_index = (mouse_y // (IMAGE_SIZE + GAP)) * MAX_IMAGES_PER_ROW + (
                    mouse_x // (IMAGE_SIZE + GAP)
                )
                if clicked_index < num_images:
                    return image_paths[clicked_index]


# Main function
def main():
    # Check if image paths are provided
    if len(sys.argv) < 2:
        print("Usage: ./image_selector.py <image1> <image2> ...")
        sys.exit(1)

    # Load images
    image_paths = sys.argv[1:]
    images = load_images(image_paths)

    # Set up display
    screen = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption("Image Selector")

    # Display gallery and get selected image path
    selected_image_path = display_gallery(screen, images, image_paths)
    print(selected_image_path)

    # Quit Pygame
    pygame.quit()


if __name__ == "__main__":
    main()
