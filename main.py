from math import copysign
from random import randint

from entities import *

pygame.init()
pygame.display.set_caption('Game')
size = WIDTH, HEIGHT
SCREEN = pygame.display.set_mode(size)
FPS = 144

sign = lambda x, y: copysign(x, y)


def main():
    global enemies, screen2, player_pos

    clock = pygame.time.Clock()

    running = True
    paused = False
    summon_timer = 50

    screen2 = pygame.Surface(size)
    player_pos = WIDTH // 2, HEIGHT // 2
    player = Player(screen2, player_pos)

    move_up = False
    move_down = False
    move_left = False
    move_right = False
    actual_move_up = False
    actual_move_down = False
    actual_move_left = False
    actual_move_right = False

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
                    create_enemy(event.pos)
                if event.button == pygame.BUTTON_RIGHT:
                    delete_enemy(event.pos)

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

            if actual_move_up:
                player.move(*DIRECTION_UP)
            if actual_move_down:
                player.move(*DIRECTION_DOWN)
            if actual_move_left:
                player.move(*DIRECTION_LEFT)
            if actual_move_right:
                player.move(*DIRECTION_RIGHT)

            if summon_timer:
                summon_timer -= 1
            else:
                w, h = randint(10, 30), randint(10, 30)
                x, y = randint(0, WIDTH - w), randint(0, HEIGHT - h)
                vel = randint(10, 100)
                create_enemy((x, y), width=w, height=h, velocity=vel)
                summon_timer = 50

            player.update()

            offset = player.get_x() - player_pos[0], player.get_y() - player_pos[1]
            player_pos = player.get_pos()
            for enemy in enemies:
                enemy.update(enemies, offset=offset)

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
    global enemies, screen2

    enemy = Enemy(screen2, pos, pygame.Color('red'), **kwargs)
    enemies.append(enemy)


def delete_enemy(pos, *args):
    global enemies
    x, y = pos
    for i in range(len(enemies)):
        w, h = enemies[i].get_size()
        x1, y1 = enemies[i].get_pos()
        if x1 - w <= x <= x1 + w and y1 - h <= y <= y1 + h:
            del enemies[i]
            break


if __name__ == '__main__':
    main()