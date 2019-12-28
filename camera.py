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
        '''if hasattr(sprite, 'x') and hasattr(sprite, 'y'):
            sprite.x += q * -(self.x - self.centerx)
            sprite.y += q * -(self.y - self.centery)'''
        '''if hasattr(sprite, 'x') and hasattr(sprite, 'y'):
            sprite.x += q * self.dx
            sprite.y += q * self.dy
            sprite.rect = sprite.rect.move(sprite.x - sprite.rect.centerx, sprite.y - sprite.rect.centery)
        else:
            sprite.rect = sprite.rect.move((round(self.dx), round(self.dy)))'''

    def normalized(self, sprite):
        new_sprite = pygame.sprite.Sprite()
        new_sprite.rect = sprite.rect.move(((self.x - self.centerx), (self.y - self.centery)))

        return new_sprite
