# для удобного создания уровней
# белый - пол, темно-желтый - стена, желтый - разрушаемый
# на клик мышью - меняется на следующий вариант, движение с зажатой кнопкой - изменяет линию на последний выбранный тип
# стрелки вправо и влево переключают между всеми создаваемыми в ЭТОТ заапуск программы картами + добавляет новую в конец
# при выходе карты сохраняются в rooms списками

import pygame

size = 10  # размер одной клетки на экране для создания, можно менять для удобства

levels = [[[1] * 48] + [[1] + [0] * 46 + [1] for i in range(46)] + [[1] * 48]]
pygame.init()
screen = pygame.display.set_mode((48 * size + 47, 48 * size + 47))
for i in range(48):
    for j in range(48):
        if levels[0][j][i] == 0:
            screen.fill((255, 255, 255), (i * (size + 1), j * (size + 1), size, size))
        elif levels[0][j][i] == 1:
            screen.fill((50, 50, 0), (i * (size + 1), j * (size + 1), size, size))
        else:
            screen.fill((150, 150, 0), (i * (size + 1), j * (size + 1), size, size))
pygame.display.flip()
running = True
hold = False
index = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            hold = True
            x, y = event.pos
            i, j = x // (size + 1), y // (size + 1)
            levels[index][j][i] = (levels[index][j][i] + 1) % 3
            color = levels[index][j][i]
            if levels[index][j][i] == 0:
                screen.fill((255, 255, 255), (i * (size + 1), j * (size + 1), size, size))
            elif levels[index][j][i] == 1:
                screen.fill((50, 50, 0), (i * (size + 1), j * (size + 1), size, size))
            else:
                screen.fill((150, 150, 0), (i * (size + 1), j * (size + 1), size, size))
            pygame.display.flip()
        if event.type == pygame.MOUSEMOTION and hold:
            x, y = event.pos
            i, j = x // (size + 1), y // (size + 1)
            levels[index][j][i] = color
            if color == 0:
                screen.fill((255, 255, 255), (i * (size + 1), j * (size + 1), size, size))
            elif color == 1:
                screen.fill((50, 50, 0), (i * (size + 1), j * (size + 1), size, size))
            else:
                screen.fill((150, 150, 0), (i * (size + 1), j * (size + 1), size, size))
            pygame.display.flip()
        if event.type == pygame.MOUSEBUTTONUP:
            hold = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                index += 1
                if index >= len(levels):
                    levels.append([[1] * 48] + [[1] + [0] * 46 + [1] for i in range(46)] + [[1] * 48])
                for i in range(48):
                    for j in range(48):
                        if levels[index][j][i] == 0:
                            screen.fill((255, 255, 255), (i * (size + 1), j * (size + 1), size, size))
                        elif levels[index][j][i] == 1:
                            screen.fill((50, 50, 0), (i * (size + 1), j * (size + 1), size, size))
                        else:
                            screen.fill((150, 150, 0), (i * (size + 1), j * (size + 1), size, size))
                pygame.display.flip()
            elif event.key == pygame.K_LEFT:
                if index > 0:
                    index -= 1
                    for i in range(48):
                        for j in range(48):
                            if levels[index][j][i] == 0:
                                screen.fill((255, 255, 255), (i * (size + 1), j * (size + 1), size, size))
                            elif levels[index][j][i] == 1:
                                screen.fill((50, 50, 0), (i * (size + 1), j * (size + 1), size, size))
                            else:
                                screen.fill((150, 150, 0), (i * (size + 1), j * (size + 1), size, size))
                    pygame.display.flip()
maps = open('rooms', 'w')
for i in range(len(levels)):
    maps.write(str(levels[i]))
    maps.write('\n\n')
