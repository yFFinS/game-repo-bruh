import pygame


class Camera:
    def __init__(self, width, height, target, centerx, centery):
        self.target = target
        self.x = target.x
        self.y = target.y
        self.w = width
        self.h = height
        self.centerx = centerx
        self.centery = centery

    def update(self):
        if self.w - self.centerx > self.target.x > self.centerx:
            self.x = self.target.x
        else:
            if self.target.x <= self.centerx:
                self.x = self.centerx
            else:
                self.x = self.w - self.centerx
        if self.h - self.centery > self.target.y > self.centery:
            self.y = self.target.y
        else:
            if self.target.y <= self.centery:
                self.y = self.centery
            else:
                self.y = self.h - self.centery

    def apply_pos(self, pos, reverse=False):
        q = 1 if not reverse else -1
        return pos[0] + q * (self.x - self.centerx), pos[1] + q * (self.y - self.centery)
    
    def apply_sprite(self, sprite, reverse=False):
        q = 1 if not reverse else -1
        sprite.rect = sprite.rect.move((q * -(self.x - self.centerx), q * -(self.y - self.centery)))
