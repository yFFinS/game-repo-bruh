from functions import *
from entities import MOVE


class Projectile(pygame.sprite.Sprite):
    def __init__(self, groups, texture, size, velocity=50, live_time=1000, damage=0, team=0, **kwargs):
        super().__init__(*groups)
        self.image = pygame.transform.scale(texture, size)
        self.rect = self.image.get_rect()
        self.timers = {'live_time': Timer(live_time, target=self.kill)}
        self.velocity = velocity
        self.damage = damage
        self.signals = {k: None for k in range(60, 70)}
        self.dx, self.dy = 0, 0
        self.x, self.y = 0, 0
        self.team = team

    def launch(self, pos1, pos2):
        angle = angle_between(pos1, pos2)
        self.dx = cos(angle)
        self.dy = sin(angle)
        self.rect.centerx, self.rect.centery = round(pos1[0]), round(pos1[1])
        self.x, self.y = pos1

    def update(self, *args):
        for timer in self.timers.values():
            timer.tick()
        self.signals[MOVE] = (self.dx, self.dy)

    def reset_signals(self):
        for signal in self.signals:
            self.signals[signal] = None

    def collision(self, group):
        collided = [sprite for sprite in pygame.sprite.spritecollide(self, group, False) if sprite.team != self.team]
        if collided:
            self.kill()
        return collided

    def get_pos(self):
        return self.x, self.y


class Fireball(Projectile):
    def __init__(self, groups, team=0):
        super().__init__(groups, PROJECTILE_TEXTURES[0], (50, 50), 350, 350, 25, team)


PROJECTILE_TEXTURES = {0: load_image('fireball.png')}
PROJECTILE_IDS = {0: Fireball}