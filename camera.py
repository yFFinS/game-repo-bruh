from main import WIDTH, HEIGHT
import pygame


class Camera:
    def __init__(self, width, height, target):
        self.target = target
        self.x = target.x
        self.y = target.y
        self.w = width
        self.h = height

    def update(self):
        if self.w - WIDTH // 2 > self.target.x > WIDTH // 2:
            self.x = self.target.x
        else:
            if self.target.x <= WIDTH // 2:
                self.x = WIDTH // 2
            else:
                self.x = self.w - WIDTH // 2
        if self.h - HEIGHT // 2 > self.target.y > HEIGHT // 2:
            self.y = self.target.y
        else:
            if self.target.y <= HEIGHT // 2:
                self.y = HEIGHT // 2
            else:
                self.y = self.h - HEIGHT // 2

    def apply_pos(self, pos, reverse=False):
        q = 1 if not reverse else -1
        return pos[0] + q * (self.x - WIDTH // 2), pos[1] + q * (self.y - HEIGHT // 2)
    
    def apply_sprite(self, sprite, reverse=False):
        q = 1 if not reverse else -1
        sprite.rect = sprite.rect.move((q * -(self.x - WIDTH // 2), q * -(self.y - HEIGHT // 2)))
        '''if hasattr(sprite, 'x') and hasattr(sprite, 'y'):
            sprite.x += q * -(self.x - WIDTH // 2)
            sprite.y += q * -(self.y - HEIGHT // 2)'''
        '''if hasattr(sprite, 'x') and hasattr(sprite, 'y'):
            sprite.x += q * self.dx
            sprite.y += q * self.dy
            sprite.rect = sprite.rect.move(sprite.x - sprite.rect.centerx, sprite.y - sprite.rect.centery)
        else:
            sprite.rect = sprite.rect.move((round(self.dx), round(self.dy)))'''

    def normalized(self, sprite):
        new_sprite = pygame.sprite.Sprite()
        new_sprite.rect = sprite.rect.move(((self.x - WIDTH // 2), (self.y - HEIGHT // 2)))

        return new_sprite
