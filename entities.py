from math import pi, sin, cos, atan, ceil
from random import random, randint

import pygame

from main import FPS, BACKGROUND


class Entity:
    def __init__(self, screen, pos, color=pygame.Color('white'), size=(10, 10), velocity=30, hp=100):
        self.screen = screen
        self.x = pos[0]
        self.y = pos[1]
        self.w, self.h = size
        self.size = size
        self.hp = hp
        self.color = color
        self.hitbox = pygame.rect.Rect([round(self.x), round(self.y), self.w, self.h])
        self.velocity = velocity
        self.sleep_timer = 0
        self.look_angle = 0

    def clear_prev(self):
        d = ceil(self.velocity / FPS)
        self.screen.blit(BACKGROUND, (self.x - d, self.y - d), (self.x - d, self.y - d, self.w + d * 2, self.h + d * 2))

    def collision(self, other):
        if type(other) == tuple:
            print(1)
            return self.hitbox.collidepoint(*other)
        if type(other) == Entity:
            return self.hitbox.colliderect(other.hitbox)
        if type(other) == list and len(other) > 1:
            return self.hitbox.collidelist(other.hitbox)

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
        self.clear_prev()
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

    def move_to(self, pos):
        dx, dy = 0, 0
        if self.y != pos[1]:
            if abs(self.y - pos[1]) < self.velocity / FPS + 1:
                self.y = pos[1]
                dx = 1 if self.x - pos[0] < 0 else -1
                dy = 0
            else:
                angle = pi / 2 - atan((self.x - pos[0]) / (self.y - pos[1]))
                dx = cos(angle)
                dy = sin(angle)
                if self.y > pos[1]:
                    dy *= -1
                    dx *= -1
        elif self.x != pos[0]:
            if abs(self.x - pos[0]) < self.velocity / FPS + 1:
                self.x = pos[0]
                dx = 0
            else:
                dx = 1 if self.x - pos[0] < 0 else -1
        self.move(dx, dy)

    def offset(self, offset):
        self.x -= offset[0]
        self.y -= offset[1]

    def update(self):
        self.update_hitbox()
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
    def __init__(self, screen, pos, color=pygame.Color('white'), size=(20, 20), velocity=300):
        super().__init__(screen, pos, color, size, velocity)


class Enemy(Entity):
    def __init__(self, screen, pos, color=pygame.Color('white'), size=(20, 20), velocity=30, hp=100, player=None,
                 team=1):
        super().__init__(screen, pos, color, size, velocity, hp)
        self.player = player
        self.fov = pi
        self.view_range = 500
        self.team = team

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

    def move_to_player(self):
        self.move_to(self.player.get_pos())

    def update(self):
        if self.sleep_timer:
            self.sleep_timer -= 1
        else:
            self.color = pygame.Color('red')
            r = random()
            if r > 0.99:
                angle = randint(0, 7)
                self.rotate(angle)

            if self.get_pos() != self.player.get_pos():
                self.move_to_player()

        self.draw()

    def sleep(self, time=100):
        self.sleep_timer = time
