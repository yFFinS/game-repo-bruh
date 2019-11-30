from math import copysign, sqrt

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

sign = lambda x, y: copysign(x, y)


class Game:
    def __init__(self):
        self.screen2 = pygame.Surface((4000, 4000))
        self.player_pos = self.screen2.get_width() // 2, self.screen2.get_height() // 2
        self.player = Player(self.screen2, self.player_pos)
        self.entities = [self.player]
        self.enemies = []
        self.camera_x, self.camera_y = -(self.screen2.get_width() - WIDTH) // 2, -(
                self.screen2.get_height() - HEIGHT) // 2
        self.main()

    def main(self):

        clock = pygame.time.Clock()

        running = True
        paused = False
        summon_timer = 50
        scale = 1

        move_up = False
        move_down = False
        move_left = False
        move_right = False

        self.screen2.blit(BACKGROUND, (0, 0))
        while running:  # Main loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        move_left = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        move_right = True
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        move_down = True
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        move_up = True
                    if event.key == pygame.K_PAUSE:
                        paused = not paused
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        move_left = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        move_right = False
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        move_down = False
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        move_up = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        self.create_enemy((event.pos[0] - 10 - self.camera_x, event.pos[1] - 10 - self.camera_y),
                                          player=self.player, size=(20, 20), velocity=60)
                    if event.button == pygame.BUTTON_RIGHT:
                        self.delete_enemy((event.pos[0] - self.camera_x, event.pos[1] - self.camera_y))
                    if event.button == pygame.BUTTON_WHEELUP:
                        scale *= 1.1
                    if event.button == pygame.BUTTON_WHEELDOWN:
                        scale *= 0.9

            if not paused:
                if move_left and move_right:
                    actual_move_left = False
                    actual_move_right = False
                else:
                    actual_move_left = move_left
                    actual_move_right = move_right
                if move_up and move_down:
                    actual_move_up = False
                    actual_move_down = False
                else:
                    actual_move_up = move_up
                    actual_move_down = move_down

                if (move_down or move_up) and (move_right or move_left):
                    pass

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
                '''if summon_timer:
                    pass
                else:
                    w, h = randint(10, 30), randint(10, 30)
                    x, y = randint(0, WIDTH - w), randint(0, HEIGHT - h)
                    vel = randint(10, 100)
                    self.create_enemy((x, y), size=(w, h), velocity=vel, player=self.player)
                    summon_timer = 50'''

                self.player.move(*move_d)
                offset = self.player.get_x() - self.player_pos[0], self.player.get_y() - self.player_pos[1]
                if BACKGROUND.get_width() - WIDTH // 2 > self.player.get_x() > WIDTH // 2:
                    self.camera_x -= offset[0]
                else:
                    if self.player.get_x() <= WIDTH // 2:
                        self.camera_x = 0
                    else:
                        self.camera_x = BACKGROUND.get_width() - WIDTH // 2
                if BACKGROUND.get_height() - HEIGHT // 2 > self.player.get_y() > HEIGHT // 2:
                    self.camera_y -= offset[1]
                else:
                    if self.player.get_y() <= HEIGHT // 2:
                        self.camera_y = 0
                    else:
                        self.camera_y = BACKGROUND.get_height() - HEIGHT // 2
                self.player_pos = self.player.get_pos()
                self.player.update()
                for enemy in self.enemies:
                    enemy.update()

            else:
                self.player.draw()
                for enemy in self.enemies:
                    enemy.draw()
            font = pygame.font.Font(None, 30)
            fps = font.render(
                'FPS: ' + str(int(clock.get_fps())) + ' Player coords: ' + str(int(self.player.get_x())) + ' ' + str(
                    int(self.player.get_y())), True, pygame.Color('green'))
            SCREEN.blit(self.screen2, (self.camera_x, self.camera_y))
            SCREEN.blit(fps, (10, 10))
            print('yes')
            pygame.display.flip()

            clock.tick(FPS)

        pygame.quit()

    def create_enemy(self, pos, **kwargs):

        enemy = Enemy(self.screen2, pos, pygame.Color('green'), **kwargs)
        self.enemies.append(enemy)
        self.entities.append(enemy)

    def delete_enemy(self, pos):
        x, y = pos
        for i in range(len(self.enemies)):
            if self.enemies[i].collision((x, y)):
                self.enemies[i].clear_prev()
                del self.entities[self.entities.index(self.enemies[i])]
                del self.enemies[i]
                break


if __name__ == '__main__':
    game = Game()
