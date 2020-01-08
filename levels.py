import pygame

levels = [[[1] * 48] + [[1] + [0] * 46 + [1] for i in range(46)] + [[1] * 48]]
pygame.init()
screen = pygame.display.set_mode((48 * 10 + 47, 48 * 10 + 47))
for i in range(48):
    for j in range(48):
        if levels[0][j][i] == 0:
            screen.fill((255, 255, 255), (i * 11, j * 11, 10, 10))
        elif levels[0][j][i] == 1:
            screen.fill((50, 50, 0), (i * 11, j * 11, 10, 10))
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            i, j = x // 11, y // 11
            levels[-1][j][i] = (levels[-1][j][i] + 1) % 3
            if levels[-1][j][i] == 0:
                screen.fill((255, 255, 255), (i * 11, j * 11, 10, 10))
            elif levels[-1][j][i] == 1:
                screen.fill((50, 50, 0), (i * 11, j * 11, 10, 10))
            else:
                screen.fill((150, 150, 0), (i * 11, j * 11, 10, 10))
            pygame.display.flip()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                levels.append([[1] * 48] + [[1] + [0] * 46 + [1] for i in range(46)] + [[1] * 48])
                for i in range(48):
                    for j in range(48):
                        if levels[-1][j][i] == 0:
                            screen.fill((255, 255, 255), (i * 11, j * 11, 10, 10))
                        elif levels[-1][j][i] == 1:
                            screen.fill((50, 50, 0), (i * 11, j * 11, 10, 10))
                pygame.display.flip()
print(*levels, sep='\n')