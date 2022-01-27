import pygame
import random
from settings import *


class Wall:
    def __init__(self, parent_surface, parent_game):
        self.parent_surface = parent_surface
        self.parent_game = parent_game
        self.image = pygame.image.load("resources/imgs/grey-e6e6e6-10x10.png").convert()
        self.image = pygame.transform.scale(self.image, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.coords = set(tuple())
        self.random_gen(Global.WALL_MAX_COUNT_IN_THOUSANDTHS)

    def random_gen(self, value_in_thousandths):
        wall_block_count = int(value_in_thousandths / 1000 * Global.GRID_COL * Global.GRID_ROW)

        for _ in range(wall_block_count):
            self.coords.add((
                random.randrange(
                    Global.LEFT_PADDING, Global.SCREEN_SIZE[0] - Global.RIGHT_PADDING, Global.BLOCK_SIZE),
                random.randrange(
                    Global.TOP_PADDING, Global.SCREEN_SIZE[1] - Global.BOTTOM_PADDING, Global.BLOCK_SIZE)))

    def draw(self):
        for coord in self.coords:
            self.parent_surface.blit(self.image, (coord[0], coord[1]))

    def reset(self):
        self.coords = set(tuple())
        self.random_gen(Global.WALL_MAX_COUNT_IN_THOUSANDTHS)
