from math import copysign
from random import random, choice
from threading import Thread
from time import sleep

from entities import *

pygame.init()
size = WIDTH, HEIGHT
SCREEN = pygame.display.set_mode(size)
FPS = 60

sign = lambda x, y: copysign(x, y)


def main():
    global enemies, screen2

    clock = pygame.time.Clock()

    running = True
    screen2 = pygame.Surface(size)
    player = Player(screen2, (WIDTH // 2, HEIGHT // 2))

    move_up = False
    move_down = False
    move_left = False
    move_right = False

    enemies = []

    while running: # главный цикл
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

        if move_up:
            player.move(*DIRECTION_UP)
        if move_down and not move_up:
            player.move(*DIRECTION_DOWN)
        if move_left:
            player.move(*DIRECTION_LEFT)
        if move_right and not move_left:
            player.move(*DIRECTION_RIGHT)

        player.update()
        for enemy in enemies:
            enemy.update()
        SCREEN.blit(screen2, (0, 0))
        pygame.display.flip()

        clock.tick(FPS)
        SCREEN.fill((0, 0, 0))
        screen2.fill(pygame.Color('black'))

    pygame.quit()


def create_enemy(pos, *args):
    global enemies, screen2

    assert type(pos) is tuple, 'pos argument can be only tuple'

    enemy = Enemy(screen2, pos)
    enemy.set_velocity(20)
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