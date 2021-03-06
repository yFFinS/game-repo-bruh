from math import pi, floor
from random import randint
from functions import *
from constants import *

PLAYER_TEXTURES = 'player1.png'
ENEMY_TEXTURES = {1: 'mage1.png'}


class Entity(pygame.sprite.Sprite):  # Used to create and control entities
    hurt_sound = load_sound('hurt.wav')

    def __init__(self, groups, pos, textures_dir, size, velocity=30, hp=100):  # Init
        super().__init__(*groups)
        self.signals = {k: None for k in range(60, 70)}
        self.image = pygame.transform.scale(load_image(textures_dir), size)
        self.default_image = self.image
        self.rect = self.image.get_rect()
        self.rect.centerx = round(pos[0])
        self.rect.centery = round(pos[1])
        self.bonus_spell_damage = 1
        self.x, self.y = pos[0], pos[1]
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
        self.particle_color = self.image.get_at((self.rect.w // 2, self.rect.h // 2))
        self.timers = {'sleep_timer': Timer(2),
                       'wait': Timer(3, target=self.wait, mode=1),
                       'attack_time': Timer(0.5),
                       'base_attack_time': Timer(0.1, target=self.start_attack_animation),
                       'invul_frames': Timer(0.3, target=self.change_condition,
                                             args=(INVULNERABILITY, False)),
                       'launch_time': Timer(2, target=self.change_condition,
                                            args=(CANRANGEATTACK, True)),
                       'pathfind': Timer(0.3, target=self.change_condition, args=(CANPATHFIND, True)),
                       'hp_regen': Timer(1, target=self.hp_regen, mode=1)}
        self.conditions[CANPATHFIND] = True
        self.conditions[WAITING] = True
        self.conditions[ATTACK] = False
        self.timers['wait'].start()
        self.timers['hp_regen'].start()
        self.cadr = 0
        self.which_sprite = 1

        self.hp_bar = HpBar(groups[-1], self)
        self.hp_bar.update()

    def start_attack_animation(self):
        self.timers['attack_time'].reset()
        self.timers['attack_time'].start()

    def hp_regen(self):
        self.hp = min(self.hp + self.passive_regen, self.get_max_hp())

    def push(self, dx, dy, strength):
        self.signals[PUSH] = (dx, dy, strength)

    def try_range_attack(self):
        if not self.conditions[CANRANGEATTACK]:
            return
        if distance_between(self.get_pos(), self.target.get_pos()) <= 1500:
            self.launch_projectile(self.projectile, self.target)
            self.conditions[CANRANGEATTACK] = False
            self.conditions[ATTACK] = True
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

    def hurt(self, damage, pos=(0, 0)):  # Gets damaged
        if self.conditions[INVULNERABILITY] or damage <= 0:
            return
        if is_sounds():
            Entity.hurt_sound.play()
        self.hp = max(0, self.hp - damage)
        self.signals[PARTICLE] = (self.get_pos(), (200, 0, 0), 10, -40, 0, 0, str(damage), 1)
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
        self.default_damage = 100
        self.damage = 100
        self.conditions[CANRANGEATTACK] = True
        self.timers['launch_time'].set_default_time(1)
        self.timers['launch_time'].reset()
        self.player1 = pygame.transform.scale(load_image('player1.png'), (50, 50))
        self.player2 = pygame.transform.scale(load_image('player2.png'), (50, 50))
        self.player3 = pygame.transform.scale(load_image('player3.png'), (50, 50))
        self.player4 = pygame.transform.scale(load_image('player4.png'), (50, 50))
        self.switch_cadr = 20
        self.switch_cadr_attack = 10
        self.cadr_attack = 0
        self.he_attack = False
        self.now_position = (0, 0)
        self.i_moving = False
        self.attack_sound = load_sound('attack.wav')

    def start_attacking(self):
        if not self.timers['attack_time'].is_started():
            self.timers['base_attack_time'].start()
            self.timers['attack_time'].args = (self.enemies,)

    def try_attack(self, pos):
        if not self.he_attack:
            self.cadr_attack = 0
            self.he_attack = True
            self.now_position = pos
            self.image = self.player4
            self.default_image = self.image
            self.which_sprite = 0
            if is_sounds():
                self.attack_sound.play()
        if self.cadr_attack == self.switch_cadr_attack:
            self.cadr_attack = 0
            self.he_attack = False
            self.image = self.player1
            self.which_sprite = 1
            self.cadr = 0
            self.default_image = self.image

    def try_range_attack(self, pos):
        if not self.conditions[CANRANGEATTACK]:
            return False
        self.launch_projectile(2, pos)
        self.conditions[CANRANGEATTACK] = False
        self.timers['launch_time'].start()
        return True

    def update(self):
        if not self.i_moving and not self.he_attack:
            self.image = self.player1
            self.which_sprite = 1
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 1 and not self.he_attack:
            self.image = self.player2
            self.which_sprite = 2
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 2 and not self.he_attack:
            self.image = self.player3
            self.which_sprite = 3
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 3 and not self.he_attack:
            self.image = self.player2
            self.which_sprite = 4
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 4 and not self.he_attack:
            self.image = self.player1
            self.which_sprite = 1
            self.cadr = 0
            self.default_image = self.image
        if self.he_attack:
            self.cadr_attack += 1
            self.try_attack(self.now_position)
        self.cadr += 1
        super().update()
        self.timers['hp_regen'].set_default_time(self.hp / self.get_max_hp())
        self.passive_regen = max(1, (self.get_max_hp() - self.hp) / secs(0.5))
        self.velocity = self.default_velocity * (2 - (self.hp / self.get_max_hp()))
        self.damage = self.default_damage * (2 - self.hp / self.get_max_hp())


class Enemy(Entity):  # Enemy class
    def __init__(self, *args, player=None, damage=50, level=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = player
        self.fov = 120
        self.player_pos = self.player.get_pos()
        self.view_range = 800
        self.target = self.player
        self.timers['player_near'] = Timer(3, target=self.change_condition, args=(FIGHTING, True))
        self.timers['wait'].start()
        self.damage = damage
        self.damage = round(1.05 ** (level - 1) * self.damage)
        self.hp = round(1.1 ** (level - 1) * self.hp)
        self.bonus_spell_damage = 1.1 ** (level - 1)
        self.passive_regen = self.passive_regen * 1.3 ** (level - 1)
        self.hp_bar.max_hp = self.hp
        self.hp_bar.update()
        self.velocity = self.default_velocity + 2 * level
        self.stop = 0

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
                self.attack_now()
            else:
                self.ai()

    def attack_now(self):
        if self.conditions[ATTACK]:
            if self.stop == 70:
                self.conditions[ATTACK] = False
                self.stop = 0
            self.stop += 1
        else:
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

    def hurt(self, damage, pos):  # Gets damaged
        self.change_condition(FIGHTING, True)
        super().hurt(damage, pos)


class Mage1(Enemy):
    def __init__(self, groups, pos, player=None, **kwargs):
        super().__init__(groups, pos, ENEMY_TEXTURES[1], (50, 50), 150, 150, player=player, **kwargs)
        self.conditions[CANRANGEATTACK] = True
        self.timers['launch_time'].set_default_time(1.5)
        self.timers['launch_time'].reset()
        self.mage1 = pygame.transform.scale(load_image('mage1.png'), (50, 50))
        self.mage2 = pygame.transform.scale(load_image('mage2.png'), (50, 50))
        self.mage3 = pygame.transform.scale(load_image('mage3.png'), (50, 50))
        self.mage4 = pygame.transform.scale(load_image('mage4.png'), (50, 50))
        self.mage5 = pygame.transform.scale(load_image('mage5.png'), (50, 50))
        self.he_moving = False
        self.which_sprite = 1
        self.switch_cadr = 17

    def update(self):
        if self.conditions[WAITING]:
            self.image = self.mage1
            self.which_sprite = 1
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 1:
            self.image = self.mage2
            self.which_sprite = 2
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 2:
            self.image = self.mage3
            self.which_sprite = 3
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 3:
            self.image = self.mage2
            self.which_sprite = 4
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 4:
            self.image = self.mage1
            self.which_sprite = 1
            self.cadr = 0
            self.default_image = self.image
        self.cadr += 1
        super().update()

    def ai(self):
        if self.conditions[FIGHTING]:
            if distance_between(self.get_pos(), self.target.get_pos()) > 600:
                self.move_to_target()
            else:
                self.try_range_attack()
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
        self.mage1 = pygame.transform.scale(load_image('mage1.png'), (50, 50))
        self.mage2 = pygame.transform.scale(load_image('mage2.png'), (50, 50))
        self.mage3 = pygame.transform.scale(load_image('mage3.png'), (50, 50))
        self.mage4 = pygame.transform.scale(load_image('mage4.png'), (50, 50))
        self.mage5 = pygame.transform.scale(load_image('mage5.png'), (50, 50))
        self.he_moving = False
        self.which_sprite = 1
        self.switch_cadr = 17

    def update(self):
        if self.conditions[WAITING]:
            self.image = self.mage1
            self.which_sprite = 1
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 1:
            self.image = self.mage2
            self.which_sprite = 2
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 2:
            self.image = self.mage3
            self.which_sprite = 3
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 3:
            self.image = self.mage2
            self.which_sprite = 4
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 4:
            self.image = self.mage1
            self.which_sprite = 1
            self.cadr = 0
            self.default_image = self.image
        self.cadr += 1
        super().update()



class Warrior1(Enemy):
    def __init__(self, groups, pos, player=None, **kwargs):
        super().__init__(groups, pos, ENEMY_TEXTURES[1], (50, 50), 300, 400, player=player, **kwargs)
        self.warrior1 = pygame.transform.scale(load_image('warrior1.png'), (50, 50))
        self.warrior2 = pygame.transform.scale(load_image('warrior2.png'), (50, 50))
        self.warrior3 = pygame.transform.scale(load_image('warrior3.png'), (50, 50))
        self.warrior4 = pygame.transform.scale(load_image('warrior4.png'), (50, 50))
        self.warrior5 = pygame.transform.scale(load_image('warrior5.png'), (50, 50))
        self.he_moving = False
        self.which_sprite = 1
        self.switch_cadr = 17

    def update(self):
        if self.conditions[WAITING]:
            self.image = self.warrior2
            self.which_sprite = 2
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 1:
            self.image = self.warrior2
            self.which_sprite = 2
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 2:
            self.image = self.warrior3
            self.which_sprite = 3
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 3:
            self.image = self.warrior2
            self.which_sprite = 4
            self.cadr = 0
            self.default_image = self.image
        elif self.cadr == self.switch_cadr and self.which_sprite == 4:
            self.image = self.warrior1
            self.which_sprite = 1
            self.cadr = 0
            self.default_image = self.image
        self.cadr += 1
        super().update()


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
        line = self.font.render(str(int(self.hp)) + '/' + str(int(self.max_hp)), True, (255, 255, 255))
        line_rect = line.get_rect()
        x = (self.rect.w - line_rect.w) // 2
        y = (self.rect.h - line_rect.h) // 2
        self.image.blit(line, (x, y))


ENEMY_IDS = {0: Mage1, 1: Mage2, 2: Warrior1}