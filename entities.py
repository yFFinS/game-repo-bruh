from random import random, choice

import pygame

from constants import *
from main import FPS


class Entity:
    def __init__(self, screen, pos, color='white'):
        self.screen = screen
        self.x = pos[0]
        self.y = pos[1]
        self.w = 20
        self.h = 20
        self.color = pygame.Color(color)
        self.velocity = 300

    def get_pos(self):
        return self.x, self.y

    def get_velocity(self):
        return self.velocity

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_width(self):
        return self.w

    def get_height(self):
        return self.h

    def get_size(self):
        return self.w, self.h

    def draw(self):
        pygame.draw.circle(self.screen, self.color, (round(self.x), round(self.y)), self.w)

    def move(self, dx, dy, force_move=False):
        # TODO
        # перемещение существа на dx, dy
        x1, y1 = self.get_pos()
        velocity = self.get_velocity()
        w, h = self.w, self.h
        able_to_move = True

        x2 = x1 + dx * velocity / FPS
        y2 = y1 + dy * velocity / FPS
        if not force_move:
            if x2 + w > WIDTH or x2 - w < 0 or y2 + h > HEIGHT or y2 - h < 0:
                able_to_move = False

        if able_to_move:
            self.x = x2
            self.y = y2
            self.draw()

    def update(self):
        self.draw()

    def set_velocity(self, velocity):
        self.velocity = velocity


class Player(Entity):
    def __init__(self, screen, pos):
        super().__init__(screen, pos)


class Enemy(Entity):
    def __init__(self, screen, pos):
        super().__init__(screen, pos)
        self.is_alive = True
        self.fov = 180
        self.look_direction = LOOK_UP

    def change_look_direction(self, direction):
        self.look_direction = direction

    def get_look_direction(self):
        return self.look_direction

    def rotate(self, rotate_direction):
        self.look_direction = (self.look_direction + rotate_direction) % 4

    def kill(self):
        self.is_alive = False

    def move_forward(self):
        dx = -1 if self.look_direction == 3 else 1 if self.look_direction == 1 else 0
        dy = -1 if self.look_direction == 0 else 1 if self.look_direction == 2 else 0
        self.move(dx, dy)

    def update(self):
        r = random()
        if r > 0.99:
            rotate_dir = choice([-1, 1])
            self.rotate(rotate_dir)

        look_direction = self.get_look_direction()
        self.color = (100, look_direction * 80, look_direction * 80)
        self.move_forward()

        self.draw()
