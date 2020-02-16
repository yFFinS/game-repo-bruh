from functions import *
from constants import *
import random


class Projectile(pygame.sprite.Sprite):
    def __init__(self, groups, texture, size, velocity=50, live_time=5.0, damage=0, team=0, power=200, *args, **kwargs):
        super().__init__(*groups)
        self.image = pygame.transform.scale(texture, size) if texture else pygame.Surface(size)
        self.rect = self.image.get_rect()
        self.timers = {'live_time': Timer(live_time, target=self.die)}
        self.velocity = velocity
        self.damage = round(damage)
        self.signals = {k: None for k in range(60, 70)}
        self.dx, self.dy = 0, 0
        self.x, self.y = 0, 0
        self.team = team
        self.impact_sound = None
        self.shot_sound = None
        self.mods = set(args)
        self.power = power
        self.counter = 0
        self.particle_color = self.image.get_at((self.rect.w // 2, self.rect.h // 2))

    def launch(self, pos1, p2):
        if type(p2) is not tuple:
            pos2 = p2.get_pos()
        else:
            pos2 = p2
        angle = angle_between(pos1, pos2)
        self.dx = cos(angle)
        self.dy = sin(angle)
        self.rect.centerx, self.rect.centery = round(pos1[0]), round(pos1[1])
        self.x, self.y = pos1
        if self.shot_sound and is_sounds():
            self.shot_sound.play()

    def update(self, *args):
        for timer in self.timers.values():
            timer.tick()
        self.move()
        if not isinstance(self, SightChecker):
            self.counter += 1
            if self.counter % 4 == 0:
                self.signals[PARTICLE] = (self.get_pos(), self.particle_color, 20, 20, random.randint(-20, 20), random.randint(-20, 20), '', 1)
                self.counter = 0

    def move(self):
        self.signals[MOVE] = (self.dx, self.dy)

    def reset_signals(self):
        for signal in self.signals:
            self.signals[signal] = None

    def collision(self, group):
        collided = [sprite for sprite in pygame.sprite.spritecollide(self, group, False) if sprite.team != self.team]
        if collided:
            self.die()
        return collided

    def get_pos(self):
        return self.x, self.y

    def die(self):
        if self.impact_sound and is_sounds():
            self.impact_sound.play()
        self.kill()


class HomingProjectile(Projectile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = None

    def launch(self, pos1, target):
        self.rect.centerx, self.rect.centery = round(pos1[0]), round(pos1[1])
        self.x, self.y = pos1
        self.target = target

    def move(self):
        self.signals[MOVETO] = self.target.get_pos()


class SightChecker(Projectile):
    def __init__(self, group, team=0, damage_amp=1, parent=None):
        super().__init__(group, PROJECTILE_TEXTURES[0], (1, 1), 1000, 0.2, 0, team)
        self.parent = parent


class Fireball(Projectile):
    damage = 100

    def __init__(self, groups, damage_amp=1, team=0):
        super().__init__(groups, PROJECTILE_TEXTURES[0], (30, 30), 450, 2, 100 * damage_amp, team)
        self.shot_sound = load_sound('fireball_shot.wav')
        self.impact_sound = load_sound('fireball_explosion.wav')


class Skull(HomingProjectile):
    damage = 250

    def __init__(self, groups, damage_amp=1, team=0):
        super().__init__(groups, PROJECTILE_TEXTURES[1], (60, 60), 50, 10, 250 * damage_amp, team)
        self.mods = {TRANSPARENT}


PROJECTILE_TEXTURES = {0: load_image('fireball.png'), 1: load_image('skull.png')}
PROJECTILE_IDS = {-1: SightChecker, 0: Fireball, 1: Skull}