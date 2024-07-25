import random

import pygame

from grid import Grid
from settings import Global


class Wall:
    def __init__(self, grid: Grid) -> None:
        self._grid: Grid = grid
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/grey-e6e6e6-10x10.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.coords: set[tuple] = set()
        self.random_gen(Global.WALL_COUNT_IN_THOUSANDTHS)

    def reset(self) -> None:
        self.coords.clear()
        self.random_gen(Global.WALL_COUNT_IN_THOUSANDTHS)

    def random_gen(self, value_in_thousandths: float) -> None:
        wall_block_count = int(value_in_thousandths / 1000 * Global.GRID_COL * Global.GRID_ROW)

        for _ in range(wall_block_count):
            while True:
                new_x = random.randint(0, Global.GRID_COL - 1)
                new_y = random.randint(0, Global.GRID_ROW - 1)
                if self._grid.has_body(new_x, new_y) or (new_x, new_y) in self.coords:
                    continue
                self.coords.add((new_x, new_y))
                break

        for coord in self.coords:
            self._grid.set_type(coord[0], coord[1], 'wall')

    def draw(self, surface: pygame.Surface) -> None:
        for coord in self.coords:
            surface.blit(
                self.image,
                (coord[0] * Global.BLOCK_SIZE + Global.LEFT_PADDING,
                 coord[1] * Global.BLOCK_SIZE + Global.TOP_PADDING)
            )
