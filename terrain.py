import random

import pygame

from functions import load_image

TILE_SIZE = 50


def neighbours(grid, x, y):
    return set([grid[y + dy][x + dx] for dx in [-1, 0, 1] if -1 < x + dx < len(grid[0]) for dy in [-1, 0, 1] if -1 < y + dy < len(grid)])


def generate_terrain(width, height):
    grid = [[0] * width for _ in range(height)]
    for x in range(width):
        for y in range(height):
            if random.random() < 0.05:
                grid[y][x] = 2
    for x in range(width):
        for y in range(height):
            nb = neighbours(grid, x, y)
            if 2 in nb:
                if random.random() < 0.35:
                    grid[y][x] = 2
                else:
                    grid[y][x] = 1
    return grid


class Terrain:
    def __init__(self, width_tiles, height_tiles):
        self.width = width_tiles
        self.height = height_tiles
        self.tile_size = TILE_SIZE
        self.grid = self.random_terrain()
        self.grid[27][27] = TILES[1]
        self.chunks = [[Chunk((16 * TILE_SIZE * x, 16 * TILE_SIZE * y),
                              [[self.grid[i][j] for j in range(16 * x, 16 * (x + 1))] for i in
                               range(16 * y, 16 * (y + 1))])
                        for y in range(width_tiles // 16)] for x in range(height_tiles // 16)]

    def get_width(self):
        return self.width * self.tile_size

    def get_height(self):
        return self.height * self.tile_size

    def random_terrain(self):
        terrain = generate_terrain(self.width, self.height)
        return [[TILES[terrain[y][x]] for x in range(self.width)] for y in range(self.height)]


class Tile:
    def __init__(self, texture, transparent=True, **kwargs):
        self.image = pygame.transform.scale(load_image(texture), (TILE_SIZE, TILE_SIZE))
        self.transparent = transparent


class Chunk(pygame.sprite.Sprite):
    def __init__(self, pos, matrix):
        super().__init__()
        self.image = pygame.Surface((16 * TILE_SIZE, 16 * TILE_SIZE))
        for x in range(16):
            for y in range(16):
                self.image.blit(matrix[y][x].image, (x * TILE_SIZE, y * TILE_SIZE))
        pygame.draw.polygon(self.image, pygame.Color('black'),
                            [(0, 0), (0, 16 * TILE_SIZE), (16 * TILE_SIZE, 16 * TILE_SIZE), (16 * TILE_SIZE, 0)], 2)
        self.rect = self.image.get_rect()
        self.rect.move_ip(pos)

    def get_pos(self):
        return self.rect.x, self.rect.y


TILES = {0: Tile('grass.jpg', True), 1: Tile('dirt.jpg', True), 2: Tile('sand.jpg', True), 3: Tile('wall.png', False)}
