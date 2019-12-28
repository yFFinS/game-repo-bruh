from main import WIDTH, HEIGHT


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

    def fix_sprite(self, sprite):
        if hasattr(sprite, 'x') and hasattr(sprite, 'y'):
            sprite.x += -(self.x - WIDTH // 2)
            sprite.y += -(self.y - HEIGHT // 2)
            sprite.rect = sprite.rect.move(round(sprite.x - sprite.rect.centerx), round(sprite.y - sprite.rect.centery))

    def apply_pos(self, pos):
        return pos[0] + self.x - WIDTH // 2, pos[1] + self.y - HEIGHT // 2
    
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
