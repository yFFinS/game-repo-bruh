import pygame
import os


def load_image(name):
    image = pygame.image.load(os.path.join('images', name)).convert_alpha()
    return image


def reverse_image(image):
    return pygame.transform.flip(image, image.get_width() // 2, 0)