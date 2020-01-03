import pygame
import os
from math import sqrt, atan2, sin, cos, degrees, radians
from random import choice
from constants import FPS


def load_image(name):
    image = pygame.image.load(os.path.join('images', name)).convert_alpha()
    return image


def reverse_image(image):
    return pygame.transform.flip(image, image.get_width() // 2, 0)


def angle_between(pos1, pos2):
    return atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])


def distance_between(pos1, pos2):
    return sqrt((pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) + (pos1[1] - pos2[1]) * (pos1[1] - pos2[1]))


class ColorMask(pygame.sprite.GroupSingle):
    def __init__(self, screen, *args):
        super().__init__(*args)
        self.screen = screen
        self.mask = pygame.sprite.Sprite()
        self.mask.image = pygame.Surface((screen.get_width(), screen.get_height()))
        self.mask.rect = self.mask.image.get_rect()
        self.mask.image.set_alpha(200)
        self.set_color((0, 0, 0))
        self.add(self.mask)

    def set_alpha(self, alpha):
        self.mask.image.set_alpha(alpha)

    def set_color(self, color):
        self.mask.image.fill(color)

    def update(self):
        self.mask.image = pygame.transform.scale(self.mask.image, (self.screen.get_width(), self.screen.get_height()))
        self.mask.rect = self.mask.image.get_rect()


class Timer:  # Timer class
    def __init__(self, time, target=None, args=tuple(), mode=0):
        self.default_time = round(FPS * time)
        self.time = self.default_time
        self.started = False
        self.mode = mode
        self.target = target
        self.args = args

    def get_time(self):
        return self.time

    def set_default_time(self, time):
        self.default_time = round(FPS * time)

    def tick(self, time=1):
        if self.time > 0:
            self.time -= time
        else:
            if self.mode == 0:
                self.stop()
            if self.target is not None:
                if self.args:
                    self.target(*self.args)
                else:
                    self.target()
                self.reset()
                return True

    def reset(self):
        self.time = self.default_time

    def start(self, time=0):
        self.started = True
        if time != 0:
            self.time = time

    def stop(self):
        self.started = False

    def is_started(self):
        return self.started