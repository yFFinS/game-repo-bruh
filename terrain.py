import random

import pygame

from constants import *
from entities import ENEMY_IDS, Enemy
from functions import load_image


def neighbours(grid, x, y):
    return set([grid[y + dy][x + dx] for dx in [-1, 0, 1] if -1 < x + dx < len(grid[0]) for dy in [-1, 0, 1] if
                -1 < y + dy < len(grid)])


def generate_terrain(width, height):
    grid = [[0] * width for _ in range(height)]
    grid[25][25] = 1
    # connect_walls(grid)
    return grid


def connect_walls(grid):
    for y in range(len(grid) - 1):
        for x in range(len(grid[0]) - 1):
            square = [grid[i][j] for i in range(y, y + 2) for j in range(x, x + 2)]
            q = 0
            if square.count(2) == 2:
                for i in square:
                    if q == 2:
                        break
                    if i == 2:
                        q += 1
                    else:
                        break
                if q != 2:
                    temp = []
                    if grid[y][x] != 2:
                        temp.append((x, y))
                    if grid[y + 1][x] != 2:
                        temp.append((x, y + 1))
                    if grid[y][x + 1] != 2:
                        temp.append((x + 1, y))
                    if grid[y + 1][x + 1] != 2:
                        temp.append((x + 1, y + 1))
                    x1, y1 = random.choice(temp)
                    grid[y1][x1] = 2


class Terrain:
    def __init__(self, width_tiles, height_tiles):
        self.width = width_tiles
        self.height = height_tiles
        self.signals = {k: None for k in range(60, 70)}

        self.bg_grid = [[TILES[0]() for x in range(self.width)] for y in range(self.height)]

        self.chambers = [[Chamber(PRESETS[1], x, y) for x in range(self.width // 48)] for y in range(self.height // 48)]

        self.obst_grid = [[TILES[-1] for i in range(self.width)] for j in range(self.height)]
        self.load_gates()
        self.load_obstacles()

        self.end_rect = pygame.rect.Rect(TILE_SIZE * 23, TILE_SIZE * 95, TILE_SIZE * 2, TILE_SIZE)

        self.chunks = [[Chunk((16 * TILE_SIZE * x, 16 * TILE_SIZE * y),
                              [[(self.bg_grid[i][j], self.obst_grid[i][j]) for j in range(16 * x, 16 * (x + 1))] for i
                               in
                               range(16 * y, 16 * (y + 1))])
                        for y in range(width_tiles // 16)] for x in range(height_tiles // 16)]

        self.walls = pygame.sprite.Group()
        self.breakables = pygame.sprite.Group()

        for pos in self.get_walls():
            wall = self.obst_grid[pos[1]][pos[0]]
            wall.rect.topleft = (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE)

        for pos in self.get_breakables():
            spr = self.obst_grid[pos[1]][pos[0]]
            spr.rect.topleft = (pos[0] * TILE_SIZE, pos[1] * TILE_SIZE)
            self.breakables.add(spr)

        self.to_update = []
        self.optimize_obstacles()

    def get_width(self):
        return self.width * TILE_SIZE

    def optimize_obstacles(self):
        self.walls = pygame.sprite.Group()
        temp = []
        for y in range(self.height):
            temp_temp = []
            for x in range(self.width):
                tile = self.obst_grid[y][x]
                if tile is not None and not isinstance(tile, Gate) and BREAKABLE not in tile.mods:
                    temp_temp.append(tile.rect)
                else:
                    temp.append(temp_temp)
                    temp_temp = []
            temp.append(temp_temp)
        for x in range(self.width):
            temp_temp = []
            for y in range(self.height):
                tile = self.obst_grid[y][x]
                if tile is not None and not isinstance(tile, Gate) and BREAKABLE not in tile.mods:
                    temp_temp.append(tile.rect)
                else:
                    temp.append(temp_temp)
                    temp_temp = []
            temp.append(temp_temp)
        for y in range(self.height):
            for x in range(self.width):
                tile = self.obst_grid[y][x]
                if tile is not None and (isinstance(tile, Gate) or BREAKABLE in tile.mods):
                    tile.topleft = (x * TILE_SIZE, y * TILE_SIZE)
                    self.walls.add(tile)
        for cur in temp:
            if cur:
                wall = pygame.sprite.Sprite()
                wall.rect = pygame.rect.Rect(*cur[0].topleft, 0, 0).unionall(cur)
                self.walls.add(wall)

    def get_height(self):
        return self.height * TILE_SIZE

    def random_terrain(self):
        terrain = generate_terrain(self.width, self.height)
        return [[TILES[terrain[y][x]] for x in range(self.width)] for y in range(self.height)]

    def get_walls(self):
        return [(x, y) for x in range(self.width)
                for y in range(self.height) if self.obst_grid[y][x] is not None]

    def get_breakables(self):
        return [(x, y) for x in range(self.width)
                for y in range(self.height) if
                self.obst_grid[y][x] is not None and BREAKABLE in self.obst_grid[y][x].mods]

    def collide(self, sprite):
        broken = pygame.sprite.spritecollide(sprite, self.breakables, False)
        to_kill = []
        for spr in broken:
            x, y = spr.rect.topleft
            for wall in self.walls:
                if wall.rect.topleft == (x, y):
                    to_kill.append(wall)
            x //= TILE_SIZE
            y //= TILE_SIZE
            self.chunks[y // 16][x // 16].change_tile(x % 16, y % 16, self.bg_grid[y][x])
            spr.kill()

        is_collided = pygame.sprite.spritecollideany(sprite, self.walls) is not None
        for wall in to_kill:
            wall.kill()
        return is_collided

    def update(self, groups, player):
        for x, y in self.to_update:
            chunk = self.chunks[x // 16][y // 16]
            chunk.update(x % 16, y % 16)
        self.to_update = []
        if self.end_rect.colliderect(player.rect):
            self.signals[END] = True
            return
        for y in range(len(self.chambers)):
            for x in range(len(self.chambers[y])):
                if self.chambers[y][x].rect.contains(player.rect):
                    if not self.chambers[y][x].visited:
                        self.chambers[y][x].start()
                        self.close_gates()
                        for x1, y1 in self.chambers[y][x].entities:
                            ent = self.chambers[y][x].entities[(x1, y1)]
                            ent(groups, (x1 + x * TILE_SIZE * 48, y1 + y * TILE_SIZE * 48), player=player)
                        break
                    elif not self.chambers[y][x].completed:
                        left = sum(1 if isinstance(ent, Enemy) else 0 for ent in groups[0])
                        if left == 0:
                            self.open_gates()
                            self.chambers[y][x].completed = True
                            self.signals[MESSAGE] = ('Chamber completed', )

    def load_gates(self):
        self.chambers[0][0].grid[23][-1] = 3
        self.chambers[0][0].grid[24][-1] = 4

        self.chambers[0][1].grid[23][0] = 3
        self.chambers[0][1].grid[24][0] = 4
        self.chambers[0][1].grid[-1][23] = 6
        self.chambers[0][1].grid[-1][24] = 5

        self.chambers[1][1].grid[0][23] = 6
        self.chambers[1][1].grid[0][24] = 5
        self.chambers[1][1].grid[23][0] = 3
        self.chambers[1][1].grid[24][0] = 4

        self.chambers[1][0].grid[23][-1] = 3
        self.chambers[1][0].grid[24][-1] = 4
        self.chambers[1][0].grid[-1][23] = 6
        self.chambers[1][0].grid[-1][24] = 5

    def load_obstacles(self):
        for y1 in range(len(self.chambers)):
            for x1 in range(len(self.chambers[0])):
                cur_chamber = self.chambers[y1][x1].grid
                for y2 in range(len(cur_chamber)):
                    for x2 in range(len(cur_chamber[0])):
                        if cur_chamber[y2][x2] == -1:
                            continue
                        self.obst_grid[y1 * len(cur_chamber) + y2][x1 * len(cur_chamber[0]) + x2] \
                            = TILES[cur_chamber[y2][x2]]()

    def close_gates(self):
        for y in range(self.width):
            for x in range(self.height):
                if isinstance(self.obst_grid[y][x], Gate):
                    self.obst_grid[y][x].close()
                    self.to_update.append((x, y))

    def open_gates(self):
        for y in range(self.width):
            for x in range(self.height):
                if isinstance(self.obst_grid[y][x], Gate):
                    self.obst_grid[y][x].open()
                    self.to_update.append((x, y))


class Tile(pygame.sprite.Sprite):
    def __init__(self, texture, *args):
        super().__init__()
        self.image = texture
        self.rect = self.image.get_rect()
        self.mods = set(args)


class Gate(Tile):
    def __init__(self, texture, *args):
        self.images = texture
        super().__init__(self.images[1], *args)
        self.prev_rect = self.rect.copy()

    def open(self):
        self.image = self.images[0]
        if self.rect.topleft != (-100, -100):
            self.prev_rect = self.rect.copy()
        self.rect = pygame.rect.Rect([-100, -100, 0, 0])

    def close(self):
        self.image = self.images[1]
        if self.rect.topleft == (-100, -100):
            self.rect = self.prev_rect.copy()


class UpGate(Gate):
    def __init__(self, *args):
        texture = [pygame.transform.chop(TILE_TEXTURES[3], [0, 0, TILE_SIZE, 0]),
                   pygame.transform.chop(TILE_TEXTURES[3], [TILE_SIZE, 0, TILE_SIZE, 0])]
        super().__init__(texture)


class DownGate(Gate):
    def __init__(self, *args):
        texture = [pygame.transform.rotate(pygame.transform.chop(TILE_TEXTURES[3], [0, 0, TILE_SIZE, 0]), 180),
                   pygame.transform.rotate(pygame.transform.chop(TILE_TEXTURES[3], [TILE_SIZE, 0, TILE_SIZE, 0]), 180)]
        super().__init__(texture)


class LeftGate(Gate):
    def __init__(self, *args):
        texture = [pygame.transform.rotate(pygame.transform.chop(TILE_TEXTURES[3], [0, 0, TILE_SIZE, 0]), 90),
                   pygame.transform.rotate(pygame.transform.chop(TILE_TEXTURES[3], [TILE_SIZE, 0, TILE_SIZE, 0]), 90)]
        super().__init__(texture)


class RightGate(Gate):
    def __init__(self, *args):
        texture = [pygame.transform.rotate(pygame.transform.chop(TILE_TEXTURES[3], [0, 0, TILE_SIZE, 0]), -90),
                   pygame.transform.rotate(pygame.transform.chop(TILE_TEXTURES[3], [TILE_SIZE, 0, TILE_SIZE, 0]), -90)]
        super().__init__(texture)


class Chunk(pygame.sprite.Sprite):
    def __init__(self, pos, matrix):
        super().__init__()
        self.image = pygame.Surface((16 * TILE_SIZE, 16 * TILE_SIZE))
        self.matrix = matrix
        for y in range(16):
            for x in range(16):
                tile = (matrix[y][x][0], matrix[y][x][1])
                self.image.blit(tile[0].image, (x * tile[0].rect.w, y * tile[0].rect.h))
                if tile[1] is not None:
                    self.image.blit(tile[1].image, (x * tile[0].rect.w, y * tile[0].rect.h))
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos)

    def get_pos(self):
        return self.rect.x, self.rect.y

    def change_tile(self, x, y, tile):
        self.image.blit(tile.image, (tile.rect.w * x, tile.rect.h * y))

    def update(self, *args):
        if not args:
            return
        x, y = args
        tile = self.matrix[y][x]
        self.image.blit(tile[0].image, (x * TILE_SIZE, y * TILE_SIZE))
        if tile[1] is None:
            return
        self.image.blit(tile[1].image, (x * TILE_SIZE, y * TILE_SIZE))


class Floor1(Tile):
    def __init__(self, *args, **kwargs):
        super().__init__(TILE_TEXTURES[0], *args)
        self.mods.add(TRANSPARENT)


class Wall1(Tile):
    def __init__(self, *args, **kwargs):
        super().__init__(TILE_TEXTURES[1], *args)


class Box1(Tile):
    def __init__(self, *args, **kwargs):
        super().__init__(TILE_TEXTURES[2], *args)
        self.mods.add(BREAKABLE)


class Chamber:
    def __init__(self, grid, x, y):
        self.rect = pygame.rect.Rect([x * TILE_SIZE * len(grid[0]) + TILE_SIZE, y * TILE_SIZE * len(grid) + TILE_SIZE,
                                      (len(grid[0]) - 2) * TILE_SIZE, (len(grid) - 2) * TILE_SIZE])
        self.grid = [[grid[y][x] for x in range(len(grid[y]))] for y in range(len(grid))]
        self.entities = dict()
        self.visited = False
        self.completed = False

    def start(self):
        self.visited = True
        amount = random.randint(6, 12)
        while len(self.entities) != amount:
            x, y = random.randint(1, len(self.grid[0]) - 1), random.randint(1, len(self.grid) - 1)
            if self.grid[y][x] == -1:
                self.entities[(TILE_SIZE * x + TILE_SIZE // 2, TILE_SIZE * y + TILE_SIZE // 2)] = random.choice(ENEMY_IDS)


TILE_TEXTURES = {0: load_image('floor1.jpg'), 1: load_image('wall1.jpg'), 2: load_image('box1.jpg'),
                 3: load_image('gate.png')}
TILES = {-1: None, 0: Floor1, 1: Wall1, 2: Box1,
         3: UpGate, 4: DownGate, 5: RightGate, 6: LeftGate}
PRESETS = {1: [[1 if i == 0 or j == 0 or j == 47 or i == 47 else -1 for j in range(48)] for i in range(48)]}
