import pygame
from entities import *
from constants import *
from math import copysign

sign = lambda x, y: copysign(x, y)


def main():
    global fps, screen2, need_to_flip
    pygame.init()

    fps = 60
    clock = pygame.time.Clock()

    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)

    screen2 = pygame.Surface(size)

    player = Player(WIDTH // 2, HEIGHT // 2)

    running = True

    move_up = False
    move_down = False
    move_left = False
    move_right = False

    need_to_flip = False

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

        if move_down:
            move(player, *DIRECTION_DOWN)
        if move_up:
            move(player, *DIRECTION_UP)
        if move_left:
            move(player, *DIRECTION_LEFT)
        if move_right:
            move(player, *DIRECTION_RIGHT)

        if need_to_flip:
            screen.blit(screen2, (0, 0))
            screen2.fill(pygame.Color('black'))
            pygame.display.flip()
            need_to_flip = False
        clock.tick(fps)
    pygame.quit()


def move(entity, dx, dy, force_move=False):
    #TODO
    global fps, screen2, need_to_flip
    # перемещение существа на dx, dy
    x1, y1 = entity.get_pos()
    velocity = entity.get_velocity()
    w, h = 20, 20
    able_to_move = True

    x2 = x1 + dx * velocity / fps
    y2 = y1 + dy * velocity / fps
    if not force_move:
        if x2 + w > WIDTH or x2 - w < 0 or y2 + h > HEIGHT or y2 - h < 0:
            able_to_move = False

    if able_to_move:
        entity.move(x2, y2)
        need_to_flip = True
        pygame.draw.circle(screen2, pygame.Color('white'), (round(x2), round(y2)), w)
    else:
        print('Cannot move further')


if __name__ == '__main__':
    main()