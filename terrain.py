import pygame


class Terrain:
    def __init__(self, width_tiles, height_tiles, tile_size=50):
        self.width = width_tiles
        self.height = height_tiles
        self.tile_size = tile_size
        self.terrain = [[0] * self.width for _ in range(self.height)]
        self.screen = None

    def get_width(self):
        return self.width * self.tile_size

    def get_height(self):
        return self.height * self.tile_size

    def set_screen(self, screen):
        self.screen = screen

    def draw(self):
        for x in range(self.width):
            for y in range(self.height):
                self.screen.blit(
                    pygame.transform.scale(TILES[self.terrain[y][x]].texture, (self.tile_size, self.tile_size)),
                    (x * self.tile_size, y * self.tile_size))

    def update_tile(self, pos, radius=1):
        for x in range(pos[0] - radius, pos[0] + radius):
            for y in range(pos[1] - radius, pos[1] + radius):
                self.screen.blit(
                    pygame.transform.scale(TILES[self.terrain[y][x]].texture, (self.tile_size, self.tile_size)),
                    (x * self.tile_size, y * self.tile_size))


class Tile:
    def __init__(self, texture_path):
        self.texture = pygame.image.load(texture_path)


TILES = {0: Tile('images/test_tile.png')}
