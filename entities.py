from random import random, choice

import pygame

from constants import *
from main import FPS


class Entity:
    def __init__(self, screen, pos, color=pygame.Color('white'), width=10, height=10, velocity=30):
        self.screen = screen
        self.x = pos[0]
        self.y = pos[1]
        self.w = width
        self.h = height
        self.color = color
        self.hitbox = pygame.rect.Rect([round(self.x), round(self.y), self.w, self.h])
        self.velocity = velocity

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
        self.update_hitbox()
        pygame.draw.rect(self.screen, self.color, self.hitbox)

    def move(self, dx, dy, entities=(), force_move=False):
        x1, y1 = self.get_pos()
        velocity = self.get_velocity()
        w, h = self.w, self.h
        able_to_move = True

        x2 = x1 + dx * velocity / FPS
        y2 = y1 + dy * velocity / FPS

        if not force_move:
            if x2 + w > WIDTH or x2 < -1 or y2 + h > HEIGHT or y2 < -1:
                able_to_move = False

        if able_to_move:
            self.x = x2
            self.y = y2
            self.draw()
            return True

    def update(self):
        self.draw()

    def update_hitbox(self):
        self.hitbox = pygame.rect.Rect([round(self.x), round(self.y), self.w, self.h])

    def set_velocity(self, velocity):
        assert type(velocity) in (int, float), 'velocity argument can be only int or float'
        self.velocity = velocity

    def set_size(self, size):
        assert type(size) is tuple, 'size argument can be only tuple'
        self.w, self.h = size


class Player(Entity):
    def __init__(self, screen, pos, color=pygame.Color('white'), width=20, height=20, velocity=300):
        super().__init__(screen, pos, color, width, height, velocity)


class Enemy(Entity):
    def __init__(self, screen, pos, color=pygame.Color('white'), width=10, height=10, velocity=30):
        super().__init__(screen, pos, color, width, height, velocity)
        self.is_alive = True
        self.sleep_timer = 0
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

    def move_forward(self, entities=()):
        dx = -1 if self.look_direction == 3 else 1 if self.look_direction == 1 else 0
        dy = -1 if self.look_direction == 0 else 1 if self.look_direction == 2 else 0
        moved = self.move(dx, dy, entities)
        if not moved:
            self.change_look_direction(choice([i for i in range(0, 4) if i != self.look_direction]))
            self.color = pygame.Color('yellow')
            self.sleep()

    def update(self, entities=()):
        if self.sleep_timer:
            self.sleep_timer -= 1
        else:
            self.color = pygame.Color('red')
            r = random()
            if r > 0.99:
                rotate_dir = choice([-1, 1])
                self.rotate(rotate_dir)

            self.move_forward(entities)

        self.draw()

    def sleep(self, time=100):
        self.sleep_timer = time
