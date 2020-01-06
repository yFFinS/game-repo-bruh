import pygame


class Menu:
    def __init__(self):
        self.buttons = pygame.sprite.Group()
        self.background_group = pygame.sprite.GroupSingle()
        self.bg = pygame.sprite.Sprite()
        self.bg.image = pygame.Surface((1000, 1000), 32)
        self.bg.rect = pygame.rect.Rect([0, 0, 1000, 1000])
        self.bg.image.set_alpha(64)
        pygame.draw.rect(self.bg.image, (0, 0, 0, 64), self.bg.rect)
        self.background_group.add(self.bg)

        self.interval = 36

    def add_button(self, text, pos=None, w=350, h=100, target=None, font_size=50, switch=False):
        if pos is None:
            if len(self.buttons):
                b = list(self.buttons)[-1]
                pos = b.rect.topleft
                pos = pos[0], pos[1] + self.interval + h
            else:
                pos = (0, 0)

        self.buttons.add(Button(text, pos, w, h, target, font_size, switch))

    def render(self, screen):
        w, h = screen.get_width(), screen.get_height()
        if self.bg.rect.w != w or self.bg.rect.h != h:
            self.bg.image = pygame.Surface((w, h), 32)
            self.bg.image.set_alpha(64)
            self.bg.rect = pygame.rect.Rect([0, 0, w, h])
            pygame.draw.rect(self.bg.image, (0, 0, 0, 64), self.bg.rect)
            self.center_buttons(w, h)
        self.background_group.draw(screen)
        self.buttons.draw(screen)

    def center_buttons(self, width, height):
        b_len = len(self.buttons)
        if b_len == 0:
            return
        for b in self.buttons:
            b.center(width, height)
        prev_b = None
        for b in self.buttons:
            if prev_b is None:
                b.rect.y = (height - (sum(i.rect.h for i in self.buttons) + self.interval * (b_len - 1))) // 2
            else:
                b.rect.y = prev_b.rect.y + self.interval + prev_b.rect.h
            prev_b = b

    def click(self, pos, type=None, button=None):
        self.buttons.update(pos, type, button)


class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos, w, h, target=None, font_size=50, switch=False):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        self.rect = pygame.rect.Rect([*pos, w, h])
        self.text = text
        self.text_color = pygame.Color('Black')
        self.font = pygame.font.Font(None, font_size)
        self.target = target
        self.switch = switch
        self.crossed = False
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
        if self.crossed:
            pygame.draw.line(self.image, pygame.Color('red'), (0, 0), (self.rect.w - 1, self.rect.h - 1), 5)
            pygame.draw.line(self.image, pygame.Color('red'), (self.rect.w - 1, 0), (0, self.rect.h - 1), 5)

    def center(self, width, height):
        self.rect.topleft = (width - self.rect.w) // 2, (height - self.rect.height) // 2

    def update(self, pos, event_type=None, event_button=None):
        if event_type == pygame.MOUSEBUTTONDOWN and event_button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(*pos):
                if not self.pressed:
                    self.pressed = True
                    self.reload_image(246)
            else:
                self.reload_image()
                self.mouse_in = False
                self.pressed = False

        if event_type == pygame.MOUSEBUTTONUP and event_button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(*pos) and self.pressed:
                self.pressed = False
                if self.switch:
                    self.crossed = not self.crossed
                self.reload_image()
                if self.target is not None:
                    self.target()
            else:
                self.reload_image()
                self.mouse_in = False
                self.pressed = False
        if event_type is None:
            if self.rect.collidepoint(*pos):
                if not self.mouse_in:
                    self.mouse_in = True
                    if not self.pressed:
                        self.reload_image(192)
            else:
                if not self.pressed:
                    self.reload_image()
                self.mouse_in = False
