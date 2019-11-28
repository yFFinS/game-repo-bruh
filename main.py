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

sign = lambda x, y: copysign(x, y)


def main():
    global enemies, screen2, player_pos, entities

    clock = pygame.time.Clock()

    running = True
    paused = False
    summon_timer = 50
    scale = 1

    screen2 = pygame.Surface(size)
    player_pos = WIDTH // 2, HEIGHT // 2
    player = Player(screen2, player_pos)

    move_up = False
    move_down = False
    move_left = False
    move_right = False

    entities = [player]
    enemies = []

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
                    create_enemy(event.pos, player=player)
                if event.button == pygame.BUTTON_RIGHT:
                    delete_enemy(event.pos)
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
            player.move(*move_d)
            if summon_timer:
                pass
            else:
                w, h = randint(10, 30), randint(10, 30)
                x, y = randint(0, WIDTH - w), randint(0, HEIGHT - h)
                vel = randint(10, 100)
                create_enemy((x, y), width=w, height=h, velocity=vel, player=player)
                summon_timer = 50

            player.update()

            offset = player.get_x() - player_pos[0], player.get_y() - player_pos[1]
            player_pos = player.get_pos()
            for enemy in enemies:
                enemy.offset(offset)
            for enemy in enemies:
                enemy.update()

        else:
            player.draw()
            for enemy in enemies:
                enemy.draw()
        font = pygame.font.Font(None, 30)
        fps = font.render('FPS: ' + str(int(clock.get_fps())), True, pygame.Color('green'))
        SCREEN.blit(screen2, (0, 0))
        SCREEN.blit(fps, (10, 10))
        pygame.display.flip()

        clock.tick(FPS)
        screen2.fill(pygame.Color('black'))

    pygame.quit()


def create_enemy(pos, **kwargs):
    global enemies, screen2, entities

    enemy = Enemy(screen2, pos, pygame.Color('red'), **kwargs)
    enemies.append(enemy)
    entities.append(enemy)


def delete_enemy(pos, *args):
    global enemies, entities
    x, y = pos
    for i in range(len(enemies)):
        w, h = enemies[i].get_size()
        x1, y1 = enemies[i].get_pos()
        if x1 - w <= x <= x1 + w and y1 - h <= y <= y1 + h:
            del entities[entities.index(enemies[i])]
            del enemies[i]
            break


def resize(k):
    global entities
    for entity in entities:
        entity.resize(k)


if __name__ == '__main__':
    main()