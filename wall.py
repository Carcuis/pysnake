import random

import pygame

from settings import Global


class Wall:
    def __init__(self) -> None:
        self.image = pygame.image.load("resources/img/grey-e6e6e6-10x10.png").convert()
        self.image = pygame.transform.scale(self.image, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.coords: set[tuple] = set()
        self.random_gen(Global.WALL_MAX_COUNT_IN_THOUSANDTHS)

    def reset(self) -> None:
        self.coords.clear()
        self.random_gen(Global.WALL_MAX_COUNT_IN_THOUSANDTHS)

    def random_gen(self, value_in_thousandths: float) -> None:
        wall_block_count = int(value_in_thousandths / 1000 * Global.GRID_COL * Global.GRID_ROW)

        for _ in range(wall_block_count):
            self.coords.add((
                random.randrange(
                    Global.LEFT_PADDING, Global.SCREEN_SIZE[0] - Global.RIGHT_PADDING, Global.BLOCK_SIZE
                ),
                random.randrange(
                    Global.TOP_PADDING, Global.SCREEN_SIZE[1] - Global.BOTTOM_PADDING, Global.BLOCK_SIZE
                )
            ))

    def draw(self, surface: pygame.Surface) -> None:
        for coord in self.coords:
            surface.blit(self.image, (coord[0], coord[1]))
