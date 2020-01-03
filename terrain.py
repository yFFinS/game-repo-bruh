import random

import pygame

from functions import load_image
from constants import *


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
        self.tile_size = TILE_SIZE
        self.bg_grid = [[TILES[0]] * self.width for _ in range(self.height)]
        self.obst_grid = [[TILES[-1]] * self.width for _ in range(self.height)]
        for i in range(10, 20):
            self.obst_grid[i][25] = TILES[1]
        for i in range(20, 30):
            self.obst_grid[25][i] = TILES[2]
        self.chunks = [[Chunk((16 * self.tile_size * x, 16 * self.tile_size * y),
                              [[(self.bg_grid[i][j], self.obst_grid[i][j])for j in range(16 * x, 16 * (x + 1))] for i in
                               range(16 * y, 16 * (y + 1))])
                        for y in range(width_tiles // 16)] for x in range(height_tiles // 16)]
        self.walls = pygame.sprite.Group()
        self.breakables = pygame.sprite.Group()
        for pos in self.get_walls():
            wall = pygame.sprite.Sprite()
            wall.rect = self.obst_grid[pos[1]][pos[0]].rect.copy()
            wall.rect.topleft = (pos[0] * self.tile_size, pos[1] * self.tile_size)
            self.walls.add(wall)
        for pos in self.get_breakables():
            spr = pygame.sprite.Sprite()
            spr.rect = self.obst_grid[pos[1]][pos[0]].rect.copy()
            spr.rect.topleft = (pos[0] * self.tile_size, pos[1] * self.tile_size)
            self.breakables.add(spr)

    def get_width(self):
        return self.width * self.tile_size

    def get_height(self):
        return self.height * self.tile_size

    def random_terrain(self):
        terrain = generate_terrain(self.width, self.height)
        return [[TILES[terrain[y][x]] for x in range(self.width)] for y in range(self.height)]

    def get_walls(self):
        return [(x, y) for x in range(self.width)
                for y in range(self.height) if self.obst_grid[y][x] is not None]

    def get_breakables(self):
        return [(x, y) for x in range(self.width)
                for y in range(self.height) if self.obst_grid[y][x] is not None and BREAKABLE in self.obst_grid[y][x].mods]

    def collide(self, sprite):
        broken = pygame.sprite.spritecollide(sprite, self.breakables, False)
        to_kill = []
        for spr in broken:
            x, y = spr.rect.topleft
            for wall in self.walls:
                if wall.rect.topleft == (x, y):
                    to_kill.append(wall)
            x //= self.tile_size
            y //= self.tile_size
            self.chunks[y // 16][x // 16].change_tile(x % 16, y % 16, self.bg_grid[y][x])
            spr.kill()

        is_collided = pygame.sprite.spritecollideany(sprite, self.walls) is not None
        for wall in to_kill:
            wall.kill()
        return is_collided


class Tile:
    def __init__(self, texture, *args):
        self.image = pygame.transform.scale(load_image(texture), (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.mods = set(args)


class Chunk(pygame.sprite.Sprite):
    def __init__(self, pos, matrix):
        super().__init__()
        self.image = pygame.Surface((16 * TILE_SIZE, 16 * TILE_SIZE))
        for x in range(16):
            for y in range(16):
                tile = (matrix[y][x][0], matrix[y][x][1])
                self.image.blit(tile[0].image, (x * tile[0].rect.w, y * tile[0].rect.h))
                if tile[1] is not None:
                    self.image.blit(tile[1].image, (x * tile[0].rect.w, y * tile[0].rect.h))
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, pygame.Color('yellow'), self.rect, 2)
        self.rect.move_ip(pos)

    def get_pos(self):
        return self.rect.x, self.rect.y

    def change_tile(self, x, y, tile):
        self.image.blit(tile.image, (tile.rect.w * x, tile.rect.h * y))


TILES = {-1: None, 0: Tile('floor1.jpg', TRANSPARENT), 1: Tile('wall1.jpg'), 2: Tile('box1.jpg', BREAKABLE)}
