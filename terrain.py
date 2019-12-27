import pygame
from functions import load_image

TILE_SIZE = 50


class Terrain:
    def __init__(self, width_tiles, height_tiles):
        self.width = width_tiles
        self.height = height_tiles
        self.tile_size = TILE_SIZE
        self.grid = [[TILES[0]] * self.width for _ in range(self.height)]
        self.grid[25][25] = TILES[1]

    def get_width(self):
        return self.width * self.tile_size

    def get_height(self):
        return self.height * self.tile_size

    def draw(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                screen.blit(self.grid[y][x].image, (x * self.tile_size, y * self.tile_size))

    def update_tile(self, screen, pos, radius=1):
        for x in range(int(pos[0]) - radius, int(pos[0]) + radius):
            for y in range(int(pos[1]) - radius, int(pos[1]) + radius):
                try:
                    screen.blit(self.grid[y][x].image, (x * self.tile_size, y * self.tile_size))
                except IndexError:
                    pass


class Tile:
    def __init__(self, texture, transparent=False, **kwargs):
        self.image = pygame.transform.scale(load_image(texture), (TILE_SIZE, TILE_SIZE))
        self.transparent = transparent


TILES = {0: Tile('grass.jpg', False), 1: Tile('wall.png', True)}
