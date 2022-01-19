import pygame
import random
from settings import *


class Wall:
    def __init__(self, parent_surface, parent_game):
        self.parent_surface = parent_surface
        self.parent_game = parent_game
        self.image = pygame.image.load("resources/imgs/grey-e6e6e6-10x10.png").convert()
        self.image = pygame.transform.scale(self.image, (BLOCK_SIZE, BLOCK_SIZE))
        self.coords = set(tuple())
        self.random_gen(WALL_MAX_COUNT_IN_THOUSANDTHS)

    def random_gen(self, value_in_thousandths):
        wall_block_count = int(value_in_thousandths / 1000 * GRID_COL * GRID_ROW)

        for _ in range(wall_block_count):
            self.coords.add((random.randrange(LEFT_PADDING, SCREEN_SIZE[0] - RIGHT_PADDING, BLOCK_SIZE),
                             random.randrange(TOP_PADDING, SCREEN_SIZE[1] - BOTTOM_PADDING, BLOCK_SIZE)))

    def draw(self):
        for coord in self.coords:
            self.parent_surface.blit(self.image, (coord[0], coord[1]))

    def reset(self):
        self.coords = set(tuple())
        self.random_gen(WALL_MAX_COUNT_IN_THOUSANDTHS)
