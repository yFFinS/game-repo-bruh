from entities import *

pygame.init()
pygame.display.set_caption('Game')
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h
size = WIDTH, HEIGHT
SCREEN = pygame.display.set_mode(size, pygame.FULLSCREEN)
FPS = 144
BACKGROUND_IMAGE = pygame.image.load('images/background.jpg')
BACKGROUND = pygame.transform.scale(BACKGROUND_IMAGE, (5000, 5000))


class Game:  # Main class
    def __init__(self):  # Init

        # FPS clock
        self.clock = pygame.time.Clock()

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        self.debugging = False
        self.running = True
        self.paused = False
        self.screen2 = pygame.Surface((BACKGROUND.get_width(), BACKGROUND.get_height()))
        self.reset()
        self.main()

    def reset(self):
        self.player_pos = self.screen2.get_width() // 2, self.screen2.get_height() // 2
        self.player = Player(self.screen2, self.player_pos)
        self.entities = [self.player]
        self.enemies = []
        self.camera_x, self.camera_y = -(self.screen2.get_width() - WIDTH) // 2, -(
                self.screen2.get_height() - HEIGHT) // 2
        self.screen2.blit(BACKGROUND, (0, 0))

    def main(self):  # Main

        while self.running:  # Main loop
            self.process_events()  # Process events

            if not self.paused:
                # Move calculation
                if self.move_left and self.move_right:
                    actual_move_left = False
                    actual_move_right = False
                else:
                    actual_move_left = self.move_left
                    actual_move_right = self.move_right
                if self.move_up and self.move_down:
                    actual_move_up = False
                    actual_move_down = False
                else:
                    actual_move_up = self.move_up
                    actual_move_down = self.move_down

                move_d = [0, 0]
                if actual_move_up:
                    move_d[1] = -1
                if actual_move_down:
                    move_d[1] = 1
                if actual_move_left:
                    if move_d[1] != 0:
                        move_d[1] /= sqrt(2)
                        move_d[0] = -1 / sqrt(2)
                    else:
                        move_d[0] = -1
                if actual_move_right:
                    if move_d[1] != 0:
                        move_d[1] /= sqrt(2)
                        move_d[0] = 1 / sqrt(2)
                    else:
                        move_d[0] = 1

                self.player.move(move_d[0], 0)
                self.player.move(0, move_d[1])

                # Camera move
                offset = self.player.get_x() - self.player_pos[0], self.player.get_y() - self.player_pos[1]
                if BACKGROUND.get_width() - WIDTH // 2 > self.player.get_x() > WIDTH // 2:
                    self.camera_x -= offset[0]
                else:
                    if self.player.get_x() <= WIDTH // 2:
                        self.camera_x = 0
                    else:
                        self.camera_x = -(BACKGROUND.get_width() - WIDTH)
                if BACKGROUND.get_height() - HEIGHT // 2 > self.player.get_y() > HEIGHT // 2:
                    self.camera_y -= offset[1]
                else:
                    if self.player.get_y() <= HEIGHT // 2:
                        self.camera_y = 0
                    else:
                        self.camera_y = -(BACKGROUND.get_height() - HEIGHT)
                self.player_pos = self.player.get_pos()

                # Updating entities
                for entity in self.entities:
                    if entity.hp == 0:
                        if type(entity) is Player:
                            self.reset()
                            break
                        del self.entities[self.entities.index(entity)]
                        del self.enemies[self.enemies.index(entity)]
                        entity.clear_prev()
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

        enemy = Enemy(self.screen2, pos, pygame.Color('green'), **kwargs)
        # Adding it to all entities
        self.enemies.append(enemy)
        self.entities.append(enemy)

    def delete_enemy(self, pos):  # Deletes enemy at pos
        x, y = pos
        for i in range(len(self.enemies)):
            if self.enemies[i].collision((x, y)):
                self.enemies[i].clear_prev()
                del self.entities[self.entities.index(self.enemies[i])]
                del self.enemies[i]
                break

    def debug(self):  # Shows debug info
        font = pygame.font.Font(None, 30)
        lines = list()
        lines.append(font.render('FPS: ' + str(int(self.clock.get_fps())), True, pygame.Color('green')))
        lines.append(font.render('Entities: ' + str(len(self.entities)), True, pygame.Color('green')))
        for attr, value in self.player.get_attribute():
            lines.append(font.render(str(attr).title() + ': ' + str(value), True, pygame.Color('green')))
        for num, line in enumerate(lines[:-3]):
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
                        self.create_enemy((event.pos[0] - 10 - self.camera_x, event.pos[1] - 10 - self.camera_y),
                                          player=self.player, size=(20, 20), velocity=60)
                    else:
                        self.player.start_attacking(self.enemies)
                if event.button == pygame.BUTTON_RIGHT:
                    self.delete_enemy((event.pos[0] - self.camera_x, event.pos[1] - self.camera_y))
                if event.button == pygame.BUTTON_WHEELUP:
                    pass
                if event.button == pygame.BUTTON_WHEELDOWN:
                    pass

            if event.type == pygame.MOUSEMOTION:
                self.player.attack_angle = 0 if event.pos[0] >= WIDTH // 2 else 180


if __name__ == '__main__':  # Main
    game = Game()
