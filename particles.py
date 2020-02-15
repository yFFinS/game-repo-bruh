from functions import *
from constants import MOVE
import random

font = pygame.font.Font(None, 30)


class Particle(pygame.sprite.Sprite):
    def __init__(self, groups, pos, color=(0, 0, 0), vx=0, vy=0, rx=0, ry=0, text=''):
        super().__init__(*groups)
        self.color = color
        self.vx = vx * 5 * random.random()
        self.vy = vy * 5 * random.random()
        self.x, self.y = pos
        self.rx = random.randint(0, round(abs(rx))) / 10
        self.ry = random.randint(0, round(abs(ry))) / 10
        if rx < 0:
            self.rx *= -1
        if ry < 0:
            self.ry *= -1
        if text:
            line = font.render(text, True, color)
            rect = line.get_rect()
            self.image = pygame.Surface((rect.w, rect.h))
            self.image.blit(line, (0, 0))
            self.image.set_colorkey((0, 0, 0))
        else:
            self.image = pygame.Surface((4, 4))
            self.image.fill(color)
        self.time = Timer(0.5, self.kill)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.signals = dict()
        self.signals[MOVE] = None

    def update(self):
        self.time.tick()
        self.signals[MOVE] = (self.vx, self.vy)
        self.vx += self.rx
        self.vy += self.ry

    def get_pos(self):
        return self.x, self.y