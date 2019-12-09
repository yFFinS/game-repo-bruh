from math import degrees

from entities import *
from terrain import *

pygame.init()
pygame.display.set_caption('Game')
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h
size = WIDTH, HEIGHT
SCREEN = pygame.display.set_mode(size, pygame.FULLSCREEN)
FPS = 40

PLAYER_TEXTURE_PATH = 'images/player.png'
ENEMIY_TEXTURE_PATHS = {1: 'images/enemy1.png'}


class Game:  # Main class
    def __init__(self):  # Init

        # FPS clock
        self.clock = pygame.time.Clock()

        self.terrain = Terrain(50, 50, 100)

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        self.debugging = False
        self.running = True
        self.paused = False
        self.screen2 = pygame.Surface((self.terrain.get_width(), self.terrain.get_height()))
        self.terrain.set_screen(self.screen2)
        self.reset()
        self.main()

    def reset(self):
        self.player_pos = self.screen2.get_width() // 2, self.screen2.get_height() // 2
        self.player = Player(self.screen2, self.player_pos, PLAYER_TEXTURE_PATH, (70, 100))
        self.player.set_attribute("velocity", 700)
        self.entities = [self.player]
        self.enemies = []
        self.camera_x, self.camera_y = -(self.screen2.get_width() - WIDTH) // 2, -(
                self.screen2.get_height() - HEIGHT) // 2
        self.terrain.draw()

    def main(self):  # Main

        while self.running:  # Main loop
            self.process_events()  # Process events

            # Screen update
            update_coords = set()
            for entity in self.entities:
                update_coords.add(entity.get_pos())
            self.update_tiles(update_coords, 2)

            if not self.paused:
                # Move calculation
                move_d = [0, 0]
                if self.move_up:
                    move_d[1] -= 1
                if self.move_down:
                    move_d[1] += 1
                if self.move_left:
                    if move_d[1] != 0:
                        move_d[1] /= sqrt(2)
                    move_d[0] -= 1 / sqrt(2)
                if self.move_right:
                    if move_d[1] != 0:
                        move_d[1] /= sqrt(2)
                    move_d[0] += 1 / sqrt(2)

                self.player.move(*move_d)

                # Camera move
                offset = self.player.get_centerx() - self.player_pos[0], self.player.get_centery() - self.player_pos[1]
                if self.screen2.get_width() - WIDTH // 2 > self.player.get_centerx() > WIDTH // 2:
                    self.camera_x -= offset[0]
                else:
                    if self.player.get_centerx() <= WIDTH // 2:
                        self.camera_x = 0
                    else:
                        self.camera_x = -(self.screen2.get_width() - WIDTH)
                if self.screen2.get_height() - HEIGHT // 2 > self.player.get_centery() > HEIGHT // 2:
                    self.camera_y -= offset[1]
                else:
                    if self.player.get_centery() <= HEIGHT // 2:
                        self.camera_y = 0
                    else:
                        self.camera_y = -(self.screen2.get_height() - HEIGHT)
                self.player_pos = self.player.get_pos()

                # Updating entities
                for entity in self.entities:
                    if type(entity) is Enemy:
                        print(entity.invul)
                    if entity.hp == 0:
                        if type(entity) is Player:
                            self.reset()
                            break
                        del self.entities[self.entities.index(entity)]
                        del self.enemies[self.enemies.index(entity)]
                    else:
                        entity.update()

            else:
                self.player.draw()
                for entity in self.entities:
                    entity.draw()

            # Screen update
            SCREEN.blit(self.screen2, (self.camera_x, self.camera_y))
            if self.debugging:
                self.debug()
            pygame.display.flip()

            # Delay
            self.clock.tick(FPS)

        pygame.quit()

    def create_enemy(self, pos, **kwargs):  # Creates enemy at pos with given kwargs

        enemy = Enemy(self.screen2, pos, **kwargs)
        # Adding it to all entities
        self.enemies.append(enemy)
        self.entities.append(enemy)

    def update_tile(self, pos, radius=1):
        x = int(pos[0]) // self.terrain.tile_size
        y = int(pos[1]) // self.terrain.tile_size
        self.terrain.update_tile((x, y), radius)

    def update_tiles(self, pos_set, radius=1):
        temp = set()
        for pos in pos_set:
            x, y = pos
            x = int(x) // self.terrain.tile_size
            y = int(y) // self.terrain.tile_size
            temp.add((x, y))
        for pos in temp:
            self.terrain.update_tile(pos, radius)

    def delete_enemy(self, pos):  # Deletes enemy at pos
        x, y = pos
        for i in range(len(self.enemies)):
            if self.enemies[i].collision((x, y)):
                self.update_tile(self.enemies[i].get_pos(), 2)
                del self.entities[self.entities.index(self.enemies[i])]
                del self.enemies[i]
                break

    def debug(self):  # Shows debug info
        font = pygame.font.Font(None, 30)
        lines = list()
        lines.append(font.render('FPS: ' + str(int(self.clock.get_fps())), True, pygame.Color('green')))
        lines.append(font.render('Entities: ' + str(len(self.entities)), True, pygame.Color('green')))
        for attr, value in self.player.get_attribute():
            lines.append(font.render(str(attr).title() + ': ' + str(value)[:min(len(str(value)), 30)], True,
                                     pygame.Color('green')))
        for num, line in enumerate(lines):
            SCREEN.blit(line, (10, num * 30 + 10))

    def process_events(self):  # Process all events
        for event in pygame.event.get():
            # Check for quit
            if event.type == pygame.QUIT:
                self.running = False
                break

            # Check for key pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.move_left = True
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.move_right = True
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.move_down = True
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.move_up = True
                if event.key == pygame.K_F3:
                    self.debugging = not self.debugging
                if event.key == pygame.K_PAUSE:
                    self.paused = not self.paused
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break

            # Check for key released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.move_left = False
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.move_right = False
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.move_down = False
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.move_up = False

            # Check for mouse button pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.create_enemy((event.pos[0] - self.camera_x, event.pos[1] - self.camera_y),
                                          player=self.player, size=(70, 100), velocity=60,
                                          texture_path=ENEMIY_TEXTURE_PATHS[1])
                    else:
                        self.player.attack(self.enemies)
                if event.button == pygame.BUTTON_RIGHT:
                    self.delete_enemy((event.pos[0] - self.camera_x, event.pos[1] - self.camera_y))
                if event.button == pygame.BUTTON_WHEELUP:
                    pass
                if event.button == pygame.BUTTON_WHEELDOWN:
                    pass

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                mx -= self.camera_x
                my -= self.camera_y
                self.player.look_angle = (-degrees(
                    atan2(-(self.player.get_centery() - my), -(self.player.get_centerx() - mx))) + 360) % 360


if __name__ == '__main__':  # Main
    game = Game()
