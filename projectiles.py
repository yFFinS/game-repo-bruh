from functions import *
from constants import *


class Projectile(pygame.sprite.Sprite):
    def __init__(self, groups, texture, size, velocity=50, live_time=5.0, damage=0, team=0, power=200, *args):
        super().__init__(*groups)
        self.image = pygame.transform.scale(texture, size) if texture else pygame.Surface(size)
        self.rect = self.image.get_rect()
        self.timers = {'live_time': Timer(live_time, target=self.kill)}
        self.velocity = velocity
        self.damage = damage
        self.signals = {k: None for k in range(60, 70)}
        self.dx, self.dy = 0, 0
        self.x, self.y = 0, 0
        self.team = team
        self.mods = set(args)
        self.power = power

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

    def update(self, *args):
        for timer in self.timers.values():
            timer.tick()
        self.move()

    def move(self):
        self.signals[MOVE] = (self.dx, self.dy)

    def reset_signals(self):
        for signal in self.signals:
            self.signals[signal] = None

    def collision(self, group):
        collided = [sprite for sprite in pygame.sprite.spritecollide(self, group, False) if sprite.team != self.team]
        if collided:
            self.timers['live_time'].time = min(self.timers['live_time'].time, 10)
        return collided

    def get_pos(self):
        return self.x, self.y


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
    def __init__(self, group, team=0, parent=None):
        super().__init__(group, PROJECTILE_TEXTURES[0], (0, 0), 3000, 0.2, 0, team)
        self.parent = parent


class Fireball(Projectile):
    def __init__(self, groups, team=0):
        super().__init__(groups, PROJECTILE_TEXTURES[0], (50, 50), 350, 3, 1000, team)


class Skull(HomingProjectile):
    def __init__(self, groups, team=0):
        super().__init__(groups, PROJECTILE_TEXTURES[1], (60, 60), 50, 10, 200, team)
        self.mods = TRANSPARENT


PROJECTILE_TEXTURES = {0: load_image('fireball.png'), 1: load_image('skull.png')}
PROJECTILE_IDS = {-1: SightChecker, 0: Fireball, 1: Skull}