from math import pi, sin, cos, atan, atan2, floor, radians, sqrt, degrees
from random import random, randint

from items import *
from main import FPS


class Entity:  # Used to create and control entities
    def __init__(self, screen, pos, texture_path, size=(10, 10), velocity=30, hp=100):  # Init
        self.screen = screen
        self.x = pos[0] - size[0]
        self.y = pos[1] - size[1]
        self.centerx = pos[0]
        self.centery = pos[1]
        self.w, self.h = size
        self.size = size
        self.hp = hp
        self.texture = pygame.transform.scale(pygame.image.load(texture_path), size)
        self.hitbox = pygame.rect.Rect([round(self.centerx) - self.w // 2, round(self.centery) - self.h // 2,
                                        self.w, self.h])
        self.velocity = velocity
        self.default_velocity = velocity
        self.attack_speed = 1
        self.look_angle = 0
        self.weapon = Weapon('bruher', 30, attack_speed=50, attack_range=50, attack_width=30)
        self.target = None
        self.waiting = False
        self.invul = False
        self.timers = {'sleep_timer': Timer(100),
                       'wait': Timer(200, target=self.wait, mode=1),
                       'base_attack_time': Timer(10, target=self.attack, args=(self.target,)),
                       'attack_time': Timer(10000 // (self.attack_speed + self.weapon.attack_speed),
                                            target=self.attack, args=(self.target,)),
                       'clear_attack': Timer(10, target='self.clear_attack_animation'),
                       'immobile': Timer(50, target=self.restore),
                       'invul_frames': Timer(20, target=self.set_attribute, args=("invul", False))}
        self.can_move = True
        self.pushed = [False, 0, 0]

        self.attack_box = pygame.rect.Rect(
            [self.centerx - self.weapon.attack_width, self.centery,
             2 * self.weapon.attack_width,
             self.weapon.attack_range])

    def reload_texture(self):
        self.texture = pygame.transform.scale(self.texture, self.size)

    def update_attackbox(self):
        if type(self) is Player:
            dx, dy = (0, -1) if 45 <= self.look_angle <= 135 else (0, 1) if 225 <= self.look_angle <= 315 \
                else (1, 0) if (315 <= self.look_angle <= 360 or 0 <= self.look_angle <= 45) else (-1, 0)
        else:
            x = self.centerx - self.target.x
            y = self.centery - self.target.y
            dx = 1 if x <= 0 else -1
            dy = 1 if y <= 0 else -1
            if abs(x) >= abs(y):
                dy = 0
            else:
                dx = 0

        if dx == 1:
            self.attack_box = pygame.rect.Rect(
                [self.centerx, self.centery - self.weapon.attack_width, self.weapon.attack_range,
                 2 * self.weapon.attack_width])
        elif dx == -1:
            self.attack_box = pygame.rect.Rect(
                [self.centerx - self.weapon.attack_range, self.centery - self.weapon.attack_width,
                 self.weapon.attack_range,
                 2 * self.weapon.attack_width])
        elif dy == -1:
            self.attack_box = pygame.rect.Rect(
                [self.centerx - self.weapon.attack_width, self.centery - self.weapon.attack_range,
                 2 * self.weapon.attack_width,
                 self.weapon.attack_range])
        elif dy == 1:
            self.attack_box = pygame.rect.Rect(
                [self.centerx - self.weapon.attack_width, self.centery,
                 2 * self.weapon.attack_width,
                 self.weapon.attack_range])

    def attack(self, target=None):
        if target is None:
            target = self.target

        pygame.draw.rect(self.screen, pygame.Color('grey'), self.attack_box)
        if type(target) != list and type(target) != tuple:
            if self.attack_box.colliderect(target.hitbox) and not target.invul:
                target.hurt(self.weapon.damage)
        else:
            for t in target:
                if self.attack_box.colliderect(t.hitbox) and not t.invul:
                    t.hurt(self.weapon.damage)

    def try_to_attack(self):
        if self.weapon.attack_range >= self.distance(self.target.get_pos()):
            if not self.timers['base_attack_time'].is_started():
                self.timers['base_attack_time'].args = (self.target,)
                self.timers['base_attack_time'].start(10000 // (self.attack_speed + self.weapon.attack_speed) // 10)

    def collision(self, other):  # Checks for collision with point / entity / entity list
        if type(other) == tuple:
            return self.hitbox.collidepoint(*other)
        if type(other) == Entity:
            return self.hitbox.colliderect(other.hitbox)
        if type(other) == list and len(other) > 1:
            return self.hitbox.collidelist(other.hitbox)

    def distance(self, pos):  # Returns distance between self and pos
        return sqrt(
            (self.centerx - pos[0]) * (self.centerx - pos[0]) + (self.centery - pos[1]) * (self.centery - pos[1]))

    def get_hp(self):  # Returns self health points
        return self.hp

    def get_pos(self):  # Returns self pos
        return self.centerx, self.centery

    def get_velocity(self):  # Returns self velocity
        return self.velocity

    def get_centerx(self):  # Returns self x
        return self.centerx

    def get_centery(self):  # Returns self y
        return self.centery

    def get_width(self):  # Returns self width
        return self.w

    def get_height(self):  # Returns self height
        return self.h

    def get_size(self):  # Returns self size (width, height)
        return self.w, self.h

    def draw(self):  # Draws self on self.screen
        if 90 <= self.look_angle <= 270:
            self.screen.blit(self.texture, (self.x, self.y))
        else:
            self.screen.blit(pygame.transform.flip(self.texture, self.texture.get_width() // 2, 0), (self.x, self.y))

    def is_sleep(self):  # Returns True if self is sleeping
        return self.timers['sleep_timer'].is_started()

    def move(self, dx, dy, entities=(), force_move=False):  # Changes self x, y to dx, dy
        x1, y1 = self.centerx, self.centery
        velocity = self.velocity

        if force_move:
            x2 = x1 + dx * velocity / FPS
            y2 = y1 + dy * velocity / FPS
        else:
            for entity in entities:
                if entity is not self and not entity.is_sleep():
                    if self.collision(entity):
                        return
            x2 = max(self.w // 2, x1 + dx * velocity / FPS)
            x2 = min(x2, self.screen.get_width() - self.w // 2)
            y2 = max(self.h // 2, y1 + dy * velocity / FPS)
            y2 = min(y2, self.screen.get_height() - self.h // 2)

        self.centerx = x2
        self.centery = y2
        self.x = self.centerx - self.size[0] // 2
        self.y = self.centery - self.size[1] // 2
        self.draw()
        return True

    def kill(self):  # Kills self
        self.hp = 0

    def hurt(self, damage):  # Gets damaged
        self.hp = max(0, self.hp - damage)
        self.invul = True
        self.timers['invul_frames'].start()

    def move_to(self, pos, entities=(), force_move=False):  # Tries to move self to pos
        dx, dy = 0, 0
        if pos[0] >= self.centerx:
            self.look_angle = 0
        else:
            self.look_angle = 180
        if self.centery != pos[1]:
            if abs(self.centery - pos[1]) < self.velocity / FPS + 1:
                self.centery = pos[1]
                dx = 1 if self.centerx - pos[0] < 0 else -1
                dy = 0
            else:
                angle = pi / 2 - atan((self.centerx - pos[0]) / (self.centery - pos[1]))
                dx = cos(angle)
                dy = sin(angle)
                if self.centery > pos[1]:
                    dy *= -1
                    dx *= -1
        elif self.centerx != pos[0]:
            if abs(self.centerx - pos[0]) < self.velocity / FPS + 1:
                self.centerx = pos[0]
                dx = 0
            else:
                dx = 1 if self.centerx - pos[0] < 0 else -1
        self.move(dx, dy, entities, force_move)

    def update(self):  # Updates self
        self.update_hitbox()
        self.draw()

    def update_hitbox(self):  # Updates self hitbox
        self.hitbox = pygame.rect.Rect([round(self.centerx) - self.w // 2, round(self.centery) - self.h // 2,
                                        self.w, self.h])

    def push(self, dx, dy, strength):
        self.can_move = False
        self.timers['immobile'].start()
        self.velocity = strength
        self.pushed = [True, dx, dy]

    def rotate(self, angle):  # Rotates self
        self.look_angle = (self.look_angle + angle) % 360

    def random_rotation(self):
        self.rotate(randint(-180, 180))

    def sleep(self, time=100):  # Sleeps for given time
        self.timers['sleep_timer'].start(time)

    def wait(self):
        self.waiting = not self.waiting
        self.timers['wait'].default_time = randint(50, 250)
        self.timers['wait'].reset()
        self.random_rotation()

    def restore(self):
        self.can_move = True
        self.pushed = [False, 0, 0]
        self.velocity = self.default_velocity

    def set_attribute(self, attribute, value):
        assert hasattr(self, attribute), f'{self.__class__} has no attribute named {attribute}'
        setattr(self, attribute, value)

    def get_attribute(self, attribute=None):
        if attribute is not None:
            assert hasattr(self, attribute), f'{self.__class__} has no attribute named {attribute}'
            return getattr(self, attribute)
        else:
            return [(attr, self.get_attribute(attr)) for attr in self.__dict__]


class Player(Entity):  # Player class
    def __init__(self, screen, pos, texture_path, size=(20, 20), velocity=300, hp=100):
        super().__init__(screen, pos, texture_path, size, velocity, hp)

    def start_attacking(self, enemies):
        if not self.timers['base_attack_time'].is_started():
            self.timers['base_attack_time'].args = (enemies,)
            self.timers['base_attack_time'].start(10000 // (self.attack_speed + self.weapon.attack_speed) // 10)

    def hurt(self, damage):  # Gets damaged
        self.hp = max(0, self.hp - damage)
        self.invul = True
        self.timers['invul_frames'].start()

    def update(self):
        self.update_attackbox()
        for timer in self.timers.values():
            if timer.is_started():
                timer.tick()


class Enemy(Entity):  # Enemy class
    def __init__(self, screen, pos, texture_path, size=(20, 20), velocity=30, hp=100, player=None):
        super().__init__(screen, pos, texture_path, size, velocity, hp)
        self.player = player
        self.fov = 60
        self.view_range = 150
        self.target = self.player
        self.attacking = False
        self.timers['player_near'] = Timer(100, self.aggro)
        self.timers['wait'].start()

    def aggro(self):
        self.attacking = True

    def check_for_player(self):  # Checks for player in self line-of-sight
        if self.attacking:
            return
        if self.distance(self.player.get_pos()) <= 50:
            if not self.timers['player_near'].is_started():
                self.timers['player_near'].start()
        else:
            self.timers['player_near'].stop()
            self.timers['player_near'].reset()
        if (self.target.get_centerx() - self.centerx) * (self.target.get_centerx() - self.centerx) + (
                self.target.get_centery() - self.centery) * (
                self.target.get_centery() - self.centery) <= self.view_range * self.view_range:
            dist_orient = atan2(-(self.target.get_centerx() - self.centerx),
                                self.target.get_centery() - self.centery) * (180 / pi)
            ang_dist = dist_orient - (self.look_angle - 90) % 360
            ang_dist = ang_dist - 360 * floor((ang_dist + 180) * (1 / 360))
            if abs(ang_dist) <= self.fov:
                self.aggro()

    def move_forward(self):  # Moves self toward looking direction
        dx = cos(radians(self.look_angle))
        dy = sin(radians(self.look_angle))
        moved = self.move(dx, dy)
        if not moved:
            self.rotate(180)

    def move_to_target(self):  # Moves self toward target
        self.move_to(self.target.get_pos())

    def update(self):  # Updates self + AI
        self.update_attackbox()
        for timer in self.timers.values():
            if timer.is_started():
                timer.tick()

        if not self.is_sleep():
            if self.attacking:
                self.move_to_target()
                self.try_to_attack()
            else:
                if not self.waiting:
                    self.move_forward()
                self.check_for_player()

        self.update_hitbox()
        self.draw()

    def hurt(self, damage):  # Gets damaged
        self.aggro()
        super().hurt(damage)


class Timer:  # Timer class
    def __init__(self, time, target=None, args=tuple(), mode=0):
        self.default_time = time
        self.time = time
        self.started = False
        self.mode = mode
        self.target = target
        self.args = args

    def get_time(self):
        return self.time

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
