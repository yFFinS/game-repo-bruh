from math import pi, floor
from random import randint
from functions import *
from constants import *

PLAYER_TEXTURES = 'player.png'
ENEMY_TEXTURES = {1: 'enemy1.png'}


class Entity(pygame.sprite.Sprite):  # Used to create and control entities
    def __init__(self, groups, pos, textures_dir, size, velocity=30, hp=100):  # Init
        super().__init__(*groups)
        self.signals = {k: None for k in range(60, 70)}
        self.image = pygame.transform.scale(load_image(textures_dir), size)
        self.default_image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = round(pos[0]) - size[0] // 2
        self.rect.y = round(pos[1]) - size[1] // 2
        self.x, self.y = pos[0] - size[0] // 2, pos[1] - size[1] // 2
        self.hp = hp
        self.velocity = velocity
        self.default_velocity = velocity
        self.conditions = {k: False for k in range(0, 10)}
        self.attack_speed = 1
        self.look_angle = 0
        self.weapon = None
        self.target = None
        self.team = 0
        self.projectile = 0
        self.passive_regen = 1
        self.timers = {'sleep_timer': Timer(2),
                       'wait': Timer(3, target=self.wait, mode=1),
                       'attack_time': Timer(0.5),
                       'base_attack_time': Timer(0.1, target=self.start_attack_animation),
                       'invul_frames': Timer(0.3, target=self.change_condition,
                                             args=(INVULNERABILITY, False)),
                       'launch_time': Timer(2, target=self.change_condition,
                                            args=(CANRANGEATTACK, True)),
                       'pathfind': Timer(0.3, target=self.change_condition, args=(CANPATHFIND, True)),
                       'hp_regen': Timer(1, target=self.hp_regen, args=(self.passive_regen,), mode=1)}
        self.conditions[CANPATHFIND] = True
        self.timers['hp_regen'].start()

        self.hp_bar = HpBar(groups[-1], self)

    def start_attack_animation(self):
        self.timers['attack_time'].reset()
        self.timers['attack_time'].start()

    def hp_regen(self, hp):
        self.hp = min(self.hp + hp, self.get_max_hp())

    def attack(self, target=None):
        pass

    def push(self, dx, dy, strength):
        self.signals[PUSH] = (dx, dy, strength)

    def try_range_attack(self):
        if not self.conditions[CANRANGEATTACK]:
            return
        if distance_between(self.get_pos(), self.target.get_pos()) <= 1500:
            self.launch_projectile(self.projectile, self.target)
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

    def get_size(self):  # Returns self size (width, height)
        return self.rect.width, self.rect.height

    def is_sleep(self):  # Returns True if self is sleeping
        return self.timers['sleep_timer'].is_started()

    def hurt(self, damage):  # Gets damaged
        if self.conditions[INVULNERABILITY] or damage <= 0:
            return
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.signals[DEAD] = True
        self.conditions[INVULNERABILITY] = True
        self.timers['invul_frames'].start()
    
    def launch_projectile(self, projectile_id, target):
        self.signals[LAUNCH] = (projectile_id, target)

    def update(self):  # Updates self
        if -90 <= self.look_angle <= 90:
            self.image = reverse_image(self.default_image)
        else:
            self.image = self.default_image

        for timer in self.timers.values():
            if timer.is_started():
                timer.tick()
        self.hp_bar.update()
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
        self.timers['wait'].set_default_time(randint(10, 80) / 20)
        self.timers['wait'].reset()
        if not self.conditions[WAITING]:
            self.random_rotation()

    def set_attribute(self, attribute, value):
        if hasattr(self, attribute):
            setattr(self, attribute, value)

    def get_attribute(self, attribute=None):
        if attribute is not None:
            if hasattr(self, attribute):
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

    def get_max_hp(self):
        return self.hp_bar.max_hp

    def get_hp(self):
        return self.hp_bar.hp


class Player(Entity):  # Player class
    def __init__(self, groups, pos):
        super().__init__(groups, pos, PLAYER_TEXTURES, (50, 50), 300, 300)
        self.enemies = None
        self.team = -1
        self.conditions[CANRANGEATTACK] = True
        self.timers['launch_time'].set_default_time(1)
        self.timers['launch_time'].reset()

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
    def __init__(self, *args, player=None, damage=50, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = player
        self.fov = 60
        self.view_range = 600
        self.target = self.player
        self.timers['player_near'] = Timer(3, target=self.change_condition, args=(FIGHTING, True))
        self.timers['wait'].start()
        self.damage = damage

    def check_for_player(self):  # Checks for player in self line-of-sight
        if self.conditions[FIGHTING]:
            return
        if distance_between(self.player.get_pos(), self.get_pos()) <= 50:
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
                self.launch_projectile(-1, self.target.get_pos())

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


class Mage2(Mage1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.projectile = 1
        self.timers['launch_time'].set_default_time(15)
        self.timers['launch_time'].reset()


class Warrior1(Enemy):
    def __init__(self, groups, pos, player=None):
        super().__init__(groups, pos, ENEMY_TEXTURES[1], (50, 50), 100, 400, player=player)


class HpBar(pygame.sprite.Sprite):
    def __init__(self, group, parent):
        super().__init__(group)
        self.parent = parent
        self.hp = self.parent.hp
        self.max_hp = self.hp
        self.image = pygame.Surface((self.parent.rect.w + 10, 10))
        self.font = pygame.font.Font(None, 16)
        self.rect = self.image.get_rect()
        self.reload_image()

    def update(self):
        self.rect.centerx = self.parent.rect.centerx
        self.rect.y = self.parent.rect.y - 20
        if self.hp != self.parent.hp:
            self.hp = self.parent.hp
            self.reload_image()
        if not self.parent.alive():
            self.kill()

    def reload_image(self):
        self.image.fill((255, 100, 100))
        pygame.draw.rect(self.image, (0, 200, 0),
                         [0, 0, round(self.image.get_width() * self.hp / self.max_hp), self.image.get_height()])
        pygame.draw.rect(self.image, (0, 0, 0), [0, 0, self.image.get_width(), self.image.get_height()], 1)
        line = self.font.render(str(self.hp) + '/' + str(self.max_hp), True, (255, 255, 255))
        line_rect = line.get_rect()
        x = (self.rect.w - line_rect.w) // 2
        y = (self.rect.h - line_rect.h) // 2
        self.image.blit(line, (x, y))


ENEMY_IDS = {0: Mage1, 1: Mage2, 2: Warrior1}