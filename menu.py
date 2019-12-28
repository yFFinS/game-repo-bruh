import pygame


class Menu:
    def __init__(self):
        self.buttons = pygame.sprite.Group()

    def add_button(self, text, pos=None, w=350, h=100, target=None, font_size=50):
        if pos is None:
            if len(self.buttons):
                b = list(self.buttons)[-1]
                pos = b.rect.topleft
                pos = pos[0], pos[1] + 35 + h
            else:
                pos = (0, 0)

        self.buttons.add(Button(text, pos, w, h, target, font_size))

    def render(self, screen):
        self.buttons.draw(screen)

    def click(self, pos, type=None, button=None):
        self.buttons.update(pos, type, button)


class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos, w, h, target=None, font_size=50):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = pygame.rect.Rect([*pos, w, h])
        self.text = text
        self.text_color = pygame.Color('Black')
        self.font = pygame.font.Font(None, font_size)
        self.target = target
        self.pressed = False
        self.mouse_in = False
        self.reload_image()

    def reload_image(self, alpha=128):
        self.image.fill((255, 255, 255, alpha))
        pygame.draw.rect(self.image, pygame.Color('black'), [0, 0, self.rect.w, self.rect.h], 5)
        line = self.font.render(self.text, True, self.text_color)
        line_rect = line.get_rect()
        x = (self.rect.w - line_rect.w) // 2
        y = (self.rect.h - line_rect.h) // 2
        self.image.blit(line, (x, y))

    def update(self, pos, type=None, button=None):
        if self.rect.collidepoint(*pos):
            if type is None:
                if not self.mouse_in:
                    self.mouse_in = True
                    self.reload_image(192)

            if type == pygame.MOUSEBUTTONDOWN and button == pygame.BUTTON_LEFT:
                if not self.pressed:
                    self.pressed = True
                    self.reload_image(246)
            if type == pygame.MOUSEBUTTONUP and button == pygame.BUTTON_LEFT and self.pressed:
                self.pressed = False
                self.reload_image()
                if self.target is not None:
                    self.target()
        else:
            if self.mouse_in:
                self.mouse_in = False
                self.reload_image()
