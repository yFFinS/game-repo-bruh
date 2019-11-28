from math import pi, sin, cos
from random import random, randint

import pygame

from main import FPS


class Entity:
    def __init__(self, screen, pos, color=pygame.Color('white'), width=10, height=10, velocity=30, hp=100):
        self.screen = screen
        self.x = pos[0]
        self.y = pos[1]
        self.w = width
        self.h = height
        self.hp = hp
        self.color = color
        self.hitbox = pygame.rect.Rect([round(self.x), round(self.y), self.w, self.h])
        self.velocity = velocity
        self.sleep_timer = 0
        self.look_angle = 0

    def collision(self, other):
        if self.hitbox.colliderect(other.hitbox):
            return True

    def get_hp(self):
        return self.hp

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

    def is_sleep(self):
        return self.sleep_timer > 0

    def move(self, dx, dy, entities=(), force_move=False):
        x1, y1 = self.get_pos()
        velocity = self.get_velocity()
        w, h = self.w, self.h
        able_to_move = True

        x2 = x1 + dx * velocity / FPS
        y2 = y1 + dy * velocity / FPS
        if not force_move:
            for entity in entities:
                if entity is not self and not entity.is_sleep():
                    if self.collision(entity):
                        able_to_move = False
                        break

        if able_to_move:
            self.x = x2
            self.y = y2
            self.draw()
            return True

    def offset(self, offset):
        self.x -= offset[0]
        self.y -= offset[1]

    def update(self):
        self.draw()

    def update_hitbox(self):
        self.hitbox = pygame.rect.Rect([round(self.x), round(self.y), round(self.w), round(self.h)])

    def set_velocity(self, velocity):
        assert type(velocity) in (int, float), 'velocity argument can be only int or float'
        self.velocity = velocity

    def set_size(self, size):
        assert type(size) is tuple, 'size argument can be only tuple'
        self.w, self.h = size


class Player(Entity):
    def __init__(self, screen, pos, color=pygame.Color('white'), width=20, height=20, velocity=300):
        super().__init__(screen, pos, color, width, height, velocity)

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.hitbox)


class Enemy(Entity):
    def __init__(self, screen, pos, color=pygame.Color('white'), width=10, height=10, velocity=30, hp=100, player=None):
        super().__init__(screen, pos, color, width, height, velocity, hp)
        self.player = player
        self.fov = pi
        self.view_range = 500

    def rotate(self, angle):
        self.look_angle = (self.look_angle + angle)

    def kill(self):
        self.hp = 0

    def move_forward(self):
        dx = cos(self.look_angle)
        dy = sin(self.look_angle)
        moved = self.move(dx, dy)
        if not moved:
            self.color = pygame.Color('yellow')
            self.sleep()

    def update(self):
        if self.sleep_timer:
            self.sleep_timer -= 1
        else:
            self.color = pygame.Color('red')
            r = random()
            if r > 0.99:
                angle = randint(0, 7)
                self.rotate(angle)

            self.move_forward()

        self.draw()

    def sleep(self, time=100):
        self.sleep_timer = time
