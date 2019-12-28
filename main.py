import pygame

pygame.init()
pygame.display.set_caption('Game')
info = pygame.display.Info()
width = info.current_w
height = info.current_h
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.RESIZABLE, 32)
FPS = 144
PLAYER_TEXTURES = 'player.png'
ENEMY_TEXTURES = {1: 'enemy1.png'}

ALL = 20
ENTITIES = 21
CHUNKS = 22

RUNNING = 40
PAUSED = 41
DEBUGGING = 42
FULLSCREEN = 43


from entities import *
from terrain import Terrain
from camera import *
from functions import *


class Game:  # Main class
    def __init__(self):  # Init

        # FPS clock
        self.screen = screen
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()

        self.sprite_groups = None

        self.conditions = None

        self.keys_pressed = None

        self.terrain = None
        self.screen2 = None
        self.player = None
        self.camera = None
        self.reset()
        self.main()

    def player_input(self):
        if pygame.K_F3 in self.keys_pressed:
            self.conditions[DEBUGGING] = not self.conditions[DEBUGGING]
            self.keys_pressed.remove(pygame.K_F3)
        if pygame.K_PAUSE in self.keys_pressed:
            self.conditions[PAUSED] = not self.conditions[PAUSED]
            self.keys_pressed.remove(pygame.K_PAUSE)
        if pygame.K_ESCAPE in self.keys_pressed:
            self.conditions[RUNNING] = False
            self.keys_pressed.remove(pygame.K_ESCAPE)
            return
        if pygame.K_SPACE in self.keys_pressed:
            self.reset()
        if pygame.K_F11 in self.keys_pressed:
            self.fullscreen()

        if not self.conditions[PAUSED]:
            # Move calculation
            move_d = [0, 0]
            if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
                move_d[1] = -1
            if pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed:
                move_d[1] = 1
            if pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
                move_d[0] = 1
            if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
                move_d[0] = -1
            if move_d[0] > 0:
                self.player.look_angle = 0
            elif move_d[0] < 0:
                self.player.look_angle = 180
            self.move(self.player, *move_d)

    def reset(self):
        self.sprite_groups = {k: pygame.sprite.Group() for k in range(20, 30)}

        self.conditions = {k: False for k in range(40, 50)}
        self.conditions[RUNNING] = True
        self.conditions[FULLSCREEN] = True

        self.keys_pressed = []

        self.terrain = Terrain(64, 64)
        self.sprite_groups[CHUNKS] = pygame.sprite.Group(self.terrain.chunks)
        for chunk in self.sprite_groups[CHUNKS]:
            self.sprite_groups[ALL].add(chunk)
        self.screen2 = pygame.Surface((self.width, self.height), pygame.HWSURFACE, 32)
        self.player = Player((self.sprite_groups[ENTITIES], self.sprite_groups[ALL]),
                             (self.terrain.get_width() // 2, self.terrain.get_height() // 2), PLAYER_TEXTURES,
                             (50, 50), velocity=200)
        self.camera = Camera(self.terrain.get_width(), self.terrain.get_height(),
                             self.player, self.width // 2, self.height // 2)

    def resize_window(self, w, h):
        self.width, self.height = w, h
        self.screen = pygame.display.set_mode((w, h), pygame.HWSURFACE | pygame.RESIZABLE, 32)
        self.camera.centerx = self.width // 2
        self.camera.centery = self.height // 2

    def fullscreen(self):
        if self.conditions[FULLSCREEN]:
            self.resize_window(self.width, self.height)
        else:
            self.resize_window(width, height)
            self.screen = pygame.display.set_mode((width, height),
                                                  pygame.FULLSCREEN | pygame.HWSURFACE | pygame.RESIZABLE, 32)
            self.camera.centerx = self.width // 2
            self.camera.centery = self.height // 2
        self.conditions[FULLSCREEN] = not self.conditions[FULLSCREEN]

    def check_signals(self):
        if self.conditions[PAUSED]:
            return
        for entity in self.sprite_groups[ENTITIES]:
            if entity.signals[MOVE]:
                self.move(entity, *entity.signals[MOVE])
            if entity.signals[MOVE_TO]:
                self.move_to(entity, entity.signals[MOVE_TO])
            entity.reset_signals()

    def main(self):  # Main

        while self.conditions[RUNNING]:  # Main loop
            self.process_events()  # Process events

            self.player_input()

            self.camera.update()

            self.update_sprites()

            self.check_signals()

            # Screen update
            self.screen.blit(self.screen2, (0, 0))
            if self.conditions[DEBUGGING]:
                self.debug()
            pygame.display.flip()

            # Delay
            self.clock.tick(FPS)

        pygame.quit()

    def move(self, sprite, dx, dy, velocity=0, force_move=False):
        x1, y1 = sprite.get_pos()
        if velocity == 0:
            velocity = float(sprite.velocity)
        if type(sprite) is Player and (dx * dy == 1 or dx * dy == -1):
            velocity /= sqrt(2)
        if not force_move:
            x2 = max(0, min(self.terrain.get_width() - self.terrain.tile_size,
                            x1 + dx * velocity / max(self.clock.get_fps(), 5)))
            y2 = max(0, min(self.terrain.get_height() - self.terrain.tile_size,
                            y1 + dy * velocity / max(self.clock.get_fps(), 5)))
            sprite.rect.x = round(x2)
            sprite.x = x2
            if self.terrain.collide_walls(sprite):
                sprite.rect.x = round(x1)
                sprite.x = x1
                x2 = x1
            sprite.rect.y = round(y2)
            sprite.y = y2
            if self.terrain.collide_walls(sprite):
                sprite.rect.y = round(y1)
                sprite.y = y1
                y2 = y1
            collided = pygame.sprite.spritecollide(sprite, self.sprite_groups[ENTITIES], False)
            if len(collided) > 1:
                for spr in collided:
                    if spr != sprite:
                        angle = angle_between(sprite.get_pos(), spr.get_pos())
                        q = 100 / max(distance_between(sprite.get_pos(), spr.get_pos()), 5)
                        dx = cos(angle) * q
                        dy = sin(angle) * q
                        if type(spr) is Player:
                            dx /= 3
                            dy /= 3
                        if type(sprite) is Player:
                            dx *= 1
                            dy *= 1
                        spr.signals[MOVE] = (dx, dy)
                sprite.rect.x = round(x1)
                sprite.x = x1
                sprite.rect.y = round(y1)
                sprite.y = y1
        else:
            x2 = x1 + dx * velocity / max(self.clock.get_fps(), 5)
            y2 = y1 + dy * velocity / max(self.clock.get_fps(), 5)
        sprite.rect.x, sprite.rect.y = round(x2), round(y2)
        sprite.x, sprite.y = x2, y2

    def move_to(self, sprite, pos, velocity=0, force_move=False):
        if velocity == 0:
            velocity = float(sprite.velocity)
        angle = atan2(pos[1] - sprite.y, pos[0] - sprite.x)
        if hasattr(sprite, 'look_angle'):
            sprite.look_angle = degrees(angle)
        if abs(sprite.x - pos[0]) <= 0.01:
            sprite.x = pos[0]
            dx = 0
        else:
            dx = cos(angle)
        if abs(sprite.y - pos[1]) <= 0.01:
            sprite.y = pos[1]
            dy = 0
        else:
            dy = sin(angle)
        self.move(sprite, dx, dy, velocity, force_move)

    def create_enemy(self, pos, **kwargs):  # Creates enemy at pos with given kwargs
        Enemy((self.sprite_groups[ENTITIES], self.sprite_groups[ALL]), pos, **kwargs)

    def update_sprites(self):
        for sprite in self.sprite_groups[ALL]:
            self.camera.apply_sprite(sprite)
        if not self.conditions[PAUSED]:
            self.sprite_groups[ALL].update()
        visible_area = pygame.sprite.Sprite()
        visible_area.rect = pygame.rect.Rect([0, 0, self.width, self.height])
        visible_sprites = pygame.sprite.Group(pygame.sprite.spritecollide(visible_area, self.sprite_groups[ALL], False))
        visible_sprites.draw(self.screen2)
        for sprite in visible_sprites:
            visible_sprites.remove(sprite)

        for sprite in self.sprite_groups[ALL]:
            self.camera.apply_sprite(sprite, True)

    def delete_enemy(self, pos):  # Deletes enemy at pos
        x, y = pos
        for entity in self.sprite_groups[ENTITIES]:
            if entity.collision((x, y)):
                self.sprite_groups[ENTITIES].remove(entity)
                self.sprite_groups[ALL].remove(entity)
                break

    def change_camera_target(self, pos):
        for sprite in self.sprite_groups[ENTITIES]:
            if sprite.rect.collidepoint(pos):
                self.camera.target = sprite
                return

    def debug(self):  # Shows debug info
        font = pygame.font.Font(None, 30)
        lines = list()
        lines.append(font.render('FPS: ' + str(int(self.clock.get_fps())), True, pygame.Color('red')))
        lines.append(font.render('Rect: ' + str(self.player.rect), True, pygame.Color('red')))
        '''lines.append(font.render('Entities: ' + str(len(self.sprite_groups[ENTITIES])), True, pygame.Color('red')))
        for num, ent in enumerate(self.sprite_groups[ENTITIES]):
            lines.append(font.render('Entity ' + str(num) + ' ' + str(ent.get_pos()), True, pygame.Color('red')))
        for attr, value in self.player.get_attribute():
            lines.append(font.render(str(attr).title() + ': ' + str(value)[:min(len(str(value)), 30)], True,
                                     pygame.Color('red')))'''
        for num, line in enumerate(lines):
            self.screen.blit(line, (10, num * 30 + 10))

    def process_events(self):  # Process all events
        for event in pygame.event.get():
            # Check for quit
            if event.type == pygame.QUIT:
                self.conditions[RUNNING] = False
                break

            # Check for key pressed
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.append(event.key)

            # Check for key released
            if event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    del self.keys_pressed[self.keys_pressed.index(event.key)]

            # Check for mouse button pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.create_enemy(self.camera.apply_pos(event.pos), size=(50, 50),
                                          player=self.player, velocity=60,
                                          texture=ENEMY_TEXTURES[1])
                    elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.change_camera_target(self.camera.apply_pos(event.pos))
                    else:
                        self.player.start_attacking()
                if event.button == pygame.BUTTON_RIGHT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.delete_enemy(self.camera.apply_pos(event.pos))

            if event.type == pygame.VIDEORESIZE:
                if not self.conditions[FULLSCREEN]:
                    self.resize_window(event.w, event.h)


if __name__ == '__main__':
    game = Game()
