import pygame
from math import degrees, atan


pygame.init()
pygame.display.set_caption('Game')
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h
size = WIDTH, HEIGHT
screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.HWSURFACE, 32)
FPS = 100
PLAYER_TEXTURES = 'player.png'
ENEMY_TEXTURES = {1: 'enemy1.png'}

ALL = 20
ENTITIES = 21

RUNNING = 40
PAUSED = 41
DEBUGGING = 42


from entities import *
from terrain import Terrain
from camera import *
from functions import *


class Game:  # Main class
    def __init__(self):  # Init

        # FPS clock
        self.clock = pygame.time.Clock()

        self.sprite_groups = {k: pygame.sprite.Group() for k in range(20, 30)}

        self.conditions = {k: False for k in range(40, 50)}
        self.conditions[RUNNING] = True

        self.keys_pressed = []

        self.terrain = Terrain(50, 50)
        self.screen2 = pygame.Surface((self.terrain.get_width(), self.terrain.get_height()), pygame.HWSURFACE, 32)
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
        if move_d != [0, 0]:
            if move_d[0] >= 0:
                self.player.look_angle = 0
            else:
                self.player.look_angle = 180
            self.move(self.player, *move_d)

    def reset(self):
        self.player = Player((self.sprite_groups[ENTITIES], self.sprite_groups[ALL]),
                             (self.screen2.get_width() // 2, self.screen2.get_height() // 2), PLAYER_TEXTURES,
                             (50, 50), velocity=200)
        self.camera = Camera(self.screen2.get_width(), self.screen2.get_height(), self.player)
        self.terrain.draw(self.screen2)

    def check_signals(self):
        for entity in self.sprite_groups[ENTITIES]:
            if entity.signals[MOVE]:
                self.move(entity, *entity.signals[MOVE])
            if entity.signals[MOVE_TO]:
                self.move_to(entity, entity.signals[MOVE_TO])

    def main(self):  # Main

        while self.conditions[RUNNING]:  # Main loop

            dirty_pos = set()
            for sprite in self.sprite_groups[ENTITIES]:
                dirty_pos.add(sprite.get_pos())
            self.update_tiles(dirty_pos, 5)

            self.process_events()  # Process events

            self.player_input()

            self.update_sprites()
            self.check_signals()

            # Screen update
            self.camera.update()
            screen.blit(self.screen2, self.camera.blit_pos())
            if self.conditions[DEBUGGING]:
                self.debug()
            pygame.display.flip()

            # Delay
            self.clock.tick(FPS)

        pygame.quit()

    def move(self, object, dx, dy, velocity=0, force_move=False):
        x1, y1 = object.get_pos()
        if velocity == 0:
            velocity = object.velocity
        if dx * dy == 1 or dx * dy == -1:
            velocity /= sqrt(2)
        if not force_move:
            x2 = max(0, min(self.screen2.get_width(), x1 + dx * velocity / max(self.clock.get_fps(), 5)))
            y2 = max(0, min(self.screen2.get_height(), y1 + dy * velocity / max(self.clock.get_fps(), 5)))
        else:
            x2 = x1 + dx * velocity / max(self.clock.get_fps(), 5)
            y2 = y1 + dy * velocity / max(self.clock.get_fps(), 5)
        object.rect.x, object.rect.y = round(x2), round(y2)
        object.x, object.y = x2, y2

    def move_to(self, object, pos, velocity=0, force_move=False):
        dx, dy = 0, 0
        if velocity == 0:
            velocity = object.velocity
        if hasattr(object, 'look_angle'):
            object.look_angle = atan2(pos[1] - object.y, pos[0] - object.x)
        if object.centery != pos[1]:
            if abs(object.centery - pos[1]) < velocity / FPS + 1:
                object.centery = pos[1]
                dx = 1 if object.centerx - pos[0] < 0 else -1
                dy = 0
            else:
                angle = pi / 2 - atan((object.centerx - pos[0]) / (object.centery - pos[1]))
                dx = cos(angle)
                dy = sin(angle)
                if object.centery > pos[1]:
                    dy *= -1
                    dx *= -1
        elif object.centerx != pos[0]:
            if abs(object.centerx - pos[0]) < velocity / FPS + 1:
                object.centerx = pos[0]
                dx = 0
            else:
                dx = 1 if object.centerx - pos[0] < 0 else -1
        self.move(object, dx, dy, velocity, force_move)

    def create_enemy(self, pos, **kwargs):  # Creates enemy at pos with given kwargs
        Enemy((self.sprite_groups[ENTITIES], self.sprite_groups[ALL]), pos, **kwargs)

    def update_tile(self, pos, radius=1):
        x = round(pos[0]) // self.terrain.tile_size
        y = round(pos[1]) // self.terrain.tile_size
        self.terrain.update_tile((x, y), radius)

    def update_tiles(self, pos_set, radius=1):
        temp = set()
        for pos in pos_set:
            x, y = pos
            x = round(x) // self.terrain.tile_size
            y = round(y) // self.terrain.tile_size
            temp.add((x, y))
        for pos in temp:
            self.terrain.update_tile(self.screen2, pos, radius)

    def update_sprites(self):
        if not self.conditions[PAUSED]:
            for sprite_group in self.sprite_groups.values():
                sprite_group.update()
        self.sprite_groups[ALL].draw(self.screen2)

    def delete_enemy(self, pos):  # Deletes enemy at pos
        x, y = pos
        for entity in self.sprite_groups[ENTITIES]:
            if entity.collision((x, y)):
                self.sprite_groups[ENTITIES].remove(entity)
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
        lines.append(font.render('Entities: ' + str(len(self.sprite_groups[ENTITIES])), True, pygame.Color('red')))
        lines.append(font.render('Camera: ' + str(self.camera.x) + ' ' + str(self.camera.y), True, pygame.Color('red')))
        for attr, value in self.player.get_attribute():
            lines.append(font.render(str(attr).title() + ': ' + str(value)[:min(len(str(value)), 30)], True,
                                     pygame.Color('red')))
        for num, line in enumerate(lines):
            screen.blit(line, (10, num * 30 + 10))

    def process_events(self):  # Process all events
        for event in pygame.event.get():
            # Check for quit
            mpos = list(pygame.mouse.get_pos())
            mpos[0] = mpos[0] - self.camera.blit_pos()[0]
            mpos[1] = mpos[1] - self.camera.blit_pos()[1]
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
                        self.create_enemy(mpos, size=(50, 50),
                                          player=self.player, velocity=60,
                                          texture=ENEMY_TEXTURES[1])
                    elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.change_camera_target(mpos)
                    else:
                        self.player.start_attacking()
                if event.button == pygame.BUTTON_RIGHT:
                    self.delete_enemy(mpos)
                if event.button == pygame.BUTTON_WHEELUP:
                    pass
                if event.button == pygame.BUTTON_WHEELDOWN:
                    pass


if __name__ == '__main__':  # Main
    game = Game()
