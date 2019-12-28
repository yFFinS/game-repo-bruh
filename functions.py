import pygame
import os
import math


def load_image(name):
    image = pygame.image.load(os.path.join('images', name)).convert_alpha()
    return image


def reverse_image(image):
    return pygame.transform.flip(image, image.get_width() // 2, 0)


def angle_between(pos1, pos2):
    return math.atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])


def distance_between(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) + (pos1[1] - pos2[1]) * (pos1[1] - pos2[1]))