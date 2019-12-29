
from math import pi, floor
from random import randint

from functions import *

PLAYER_TEXTURES = 'player.png'
ENEMY_TEXTURES = {1: 'enemy1.png'}

WAITING = 0
INVULNERABILITY = 1
IMMOVABLE = 2
FIGHTING = 3
CANRANGEATTACK = 4

MOVE = 60
MOVETO = 61
LAUNCH = 62

SIDE = 70
UP = 71
DOWN = 72


class Entity(pygame.sprite.Sprite):  # Used to create and control entities
    def __init__(self, groups, pos, textures_dir, size, velocity=30, hp=100):  # Init
        super().__init__(*groups)
        self.signals = {k: None for k in range(60, 70)}
        self.size = size
        self.image = pygame.transform.scale(load_image(textures_dir), size)
        self.default_image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = round(pos[0]) - self.rect.width
        self.rect.y = round(pos[1]) - self.rect.height
        self.x, self.y = pos[0] - self.rect.width // 2, pos[1] - self.rect.height // 2
        self.x = round(pos[0])
        self.y = round(pos[1])
        self.hp = hp
        self.velocity = velocity
        self.default_velocity = velocity
        self.conditions = {k: False for k in range(0, 10)}
        self.attack_speed = 1
        self.look_angle = 0
        self.weapon = None
        self.target = None
        self.team = 0
        self.timers = {'sleep_timer': Timer(100),
                       'wait': Timer(200, target=self.wait, mode=1),
                       'attack_time': Timer(30),
                       'base_attack_time': Timer(10, target=self.start_attack_animation),
                       'invul_frames': Timer(20, target=self.change_condition,
                                             args=(self.conditions[INVULNERABILITY], False))}

    def start_attack_animation(self):
        self.timers['attack_time'].reset()
        self.timers['attack_time'].start()

    def attack(self, target=None):
        # TODO
        pass
        '''if target is None:
            target = self.target
        cur_frame, frames = self.timers['attack_time'].default_time - self.timers['attack_time'].time, self.timers[
            'attack_time'].default_time
        offset, rect = self.weapon.get_current_sprite(cur_frame, frames)
        if 90 <= self.look_angle <= 180:
            self.screen.blit(self.weapon.texture, (self.x - self.rect.width // 2, self.y + offset), rect)
            attack_box = pygame.rect.Rect([self.x - self.rect.width // 2, self.y + offset, *self.weapon.size])
        elif 180 <= self.look_angle <= 270:
            self.screen.blit(self.weapon.texture,
                             (self.x - self.rect.width // 2 + offset, self.y + self.rect.height // 2), rect)
            attack_box = pygame.rect.Rect([self.x - self.rect.width // 2, self.y + offset, *self.weapon.size])
        if 90 <= self.look_angle <= 180:
            self.screen.blit(self.weapon.texture, (self.x - self.rect.width // 2, self.y + offset), rect)
            attack_box = pygame.rect.Rect([self.x - self.rect.width // 2, self.y + offset, *self.weapon.size])
        if 90 <= self.look_angle <= 180:
            self.screen.blit(self.weapon.texture, (self.x - self.rect.width // 2, self.y + offset), rect)
            attack_box = pygame.rect.Rect([self.x - self.rect.width // 2, self.y + offset, *self.weapon.size])
        if cur_frame / frames == 0.4:
            if target is None:
                return
            if type(target) != list and type(target) != tuple:
                if attack_box.colliderect(target.hitbox) and not target.invul:
                    target.hurt(self.weapon.damage)
            else:
                for t in target:
                    if attack_box.colliderect(t.hitbox) and not t.invul:
                        t.hurt(self.weapon.damage)'''

    def try_to_attack(self):
        if self.weapon is None:
            return
        if self.weapon.attack_range >= distance_between(self.target.get_pos(), self.get_pos()):
            if not self.timers['base_attack_time'].is_started():
                self.timers['base_attack_time'].args = (self.target,)
                self.timers['base_attack_time'].start(10000 // (self.attack_speed + self.weapon.attack_speed) // 10)

    def try_range_attack(self):
        if not self.conditions[CANRANGEATTACK]:
            return
        if distance_between(self.get_pos(), self.target.get_pos()) <= 1500:
            self.launch_projectile(0, self.target.get_pos())
            self.conditions[CANRANGEATTACK] = False
            self.timers['launch_time'].start()
            return True

    def collision(self, other):  # Checks for collision with point / entity / entity list
        if type(other) == tuple:
            return self.rect.collidepoint(*other)
        if type(other) == Entity:
            return self.rect.colliderect(other.hitbox)
        if type(other) == list and len(other) > 1:
            return self.rect.collidelist(other.hitbox)

    def get_pos(self):  # Returns self pos
        return self.x, self.y

    def get_width(self):  # Returns self width
        return self.rect.width

    def get_height(self):  # Returns self height
        return self.rect.height

    def get_size(self):  # Returns self size (width, height)
        return self.rect.width, self.rect.height

    def is_sleep(self):  # Returns True if self is sleeping
        return self.timers['sleep_timer'].is_started()

    def hurt(self, damage):  # Gets damaged
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.kill()
            return
        self.conditions[INVULNERABILITY] = True
        self.timers['invul_frames'].start()
    
    def launch_projectile(self, projectile_id, pos):
        self.signals[LAUNCH] = (projectile_id, pos)

    def update(self):  # Updates self
        if -90 <= self.look_angle <= 90:
            self.image = reverse_image(self.default_image)
        else:
            self.image = self.default_image

        for timer in self.timers.values():
            if timer.is_started():
                timer.tick()

        if self.timers['attack_time'].is_started():
            self.attack()

    def rotate(self, angle):  # Rotates self
        self.look_angle += angle
        if self.look_angle > 180:
            self.look_angle = 180 - self.look_angle % 180
        if self.look_angle < -180:
            self.look_angle = 180 + self.look_angle % 180

    def random_rotation(self):
        self.rotate(randint(-180, 180))

    def sleep(self, time=100):  # Sleeps for given time
        self.timers['sleep_timer'].start(time)

    def wait(self):
        self.conditions[WAITING] = not self.conditions[WAITING]
        self.timers['wait'].default_time = randint(50, 250)
        self.timers['wait'].reset()
        if not self.conditions[WAITING]:
            self.random_rotation()

    def set_attribute(self, attribute, value):
        assert hasattr(self, attribute), str(self.__class__) + 'has no attribute named' + attribute
        setattr(self, attribute, value)

    def get_attribute(self, attribute=None):
        if attribute is not None:
            assert hasattr(self, attribute), f'{self.__class__} has no attribute named {attribute}'
            return getattr(self, attribute)
        else:
            return [(attr, self.get_attribute(attr)) for attr in self.__dict__]

    def change_condition(self, condition, value):
        self.conditions[condition] = value

    def reset_signals(self):
        for signal in self.signals:
            self.signals[signal] = None

    def move_from(self, pos):
        dx = -cos(angle_between(self.get_pos(), pos))
        dy = -sin(angle_between(self.get_pos(), pos))
        self.signals[MOVE] = (dx, dy)


class Player(Entity):  # Player class
    def __init__(self, groups, pos):
        super().__init__(groups, pos, PLAYER_TEXTURES, (50, 50), 300, 300)
        self.enemies = None
        self.team = 1
        self.conditions[CANRANGEATTACK] = True
        self.timers['launch_time'] = Timer(150, target=self.change_condition,
                                           args=(CANRANGEATTACK, True))

    def start_attacking(self):
        if not self.timers['attack_time'].is_started():
            self.timers['base_attack_time'].start()
            self.timers['attack_time'].args = (self.enemies,)

    def try_range_attack(self, pos):
        if not self.conditions[CANRANGEATTACK]:
            return
        self.launch_projectile(0, pos)
        self.conditions[CANRANGEATTACK] = False
        self.timers['launch_time'].start()
        return True


class Enemy(Entity):  # Enemy class
    def __init__(self, groups, pos, texture, size, velocity=30, hp=100, player=None):
        super().__init__(groups, pos, texture, size, velocity, hp)
        self.player = player
        self.fov = 60
        self.view_range = 150
        self.target = self.player
        self.attacking = False
        self.timers['player_near'] = Timer(100, target=self.change_condition, args=(FIGHTING, True))
        self.timers['wait'].start()

    def check_for_player(self):  # Checks for player in self line-of-sight
        if self.conditions[FIGHTING]:
            return
        if distance_between(self.player.get_pos(), self.get_pos()) <= 300:
            if not self.timers['player_near'].is_started():
                self.timers['player_near'].start()
        else:
            self.timers['player_near'].stop()
            self.timers['player_near'].reset()
        if (self.target.x - self.x) * (self.target.x - self.x) + (
                self.target.y - self.y) * (
                self.target.y - self.y) <= self.view_range * self.view_range:
            dist_orient = atan2(-(self.target.x - self.x),
                                self.target.y - self.y) * (180 / pi)
            ang_dist = dist_orient - (self.look_angle - 90) % 360
            ang_dist = ang_dist - 360 * floor((ang_dist + 180) * (1 / 360))
            if abs(ang_dist) <= self.fov:
                self.change_condition(FIGHTING, True)

    def move_forward(self):  # Moves self toward looking direction
        dx = cos(radians(self.look_angle))
        dy = sin(radians(self.look_angle))
        self.signals[MOVE] = (dx, dy)

    def move_to_target(self):  # Moves self toward target
        self.signals[MOVETO] = self.target.get_pos()

    def update(self):  # Updates self + AI
        super().update()
        if not self.is_sleep():
            if self.conditions[FIGHTING]:
                self.look_angle = degrees(angle_between(self.get_pos(), self.target.get_pos()))
                self.rotate(0)
            self.ai()

    def ai(self):
        if self.conditions[FIGHTING]:
            attacked = self.try_range_attack()
            if not attacked:
                self.move_to_target()
                self.try_to_attack()
        else:
            if not self.conditions[WAITING]:
                self.move_forward()
            self.check_for_player()

    def hurt(self, damage):  # Gets damaged
        self.change_condition(FIGHTING, True)
        super().hurt(damage)


class Mage1(Enemy):
    def __init__(self, groups, pos, player=None):
        super().__init__(groups, pos, ENEMY_TEXTURES[1], (50, 50), 150, 150, player=player)
        self.conditions[CANRANGEATTACK] = True
        self.timers['launch_time'] = Timer(150, target=self.change_condition,
                                           args=(CANRANGEATTACK, True))

    def ai(self):
        if self.conditions[FIGHTING]:
            attacked = self.try_range_attack()
            if not attacked:
                if distance_between(self.get_pos(), self.target.get_pos()) > 600:
                    self.move_to_target()
                if distance_between(self.get_pos(), self.target.get_pos()) < 250:
                    self.move_from(self.target.get_pos())

        else:
            if not self.conditions[WAITING]:
                self.move_forward()
            self.check_for_player()
