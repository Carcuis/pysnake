import math
import random

import pygame

from grid import Grid
from settings import Global
from snake import Snake
from util import Util


class LittleSnake(Snake):
    def __init__(self, x: int, y: int, length: int, move_speed: int, grid: Grid) -> None:
        super().__init__(grid)
        self._grid = grid
        self.direction = "down"
        self.length = length
        self.x = [x] * self.length
        self.y = [y - (i + 1) for i in range(self.length)]
        self.move_speed = move_speed


class AnimationManager:
    def __init__(self, grid: Grid) -> None:
        self._grid = grid
        self._little_fresh_snakes: list[Snake] = []
        self._little_on_screen_snakes: list[Snake] = []

        # larger grid size than self._grid, making the start-screen to completely fill up with snakes even with padding
        self._min_row = - math.ceil(Global.TOP_PADDING / Global.BLOCK_SIZE)
        self._max_row = Global.GRID_ROW + math.ceil(Global.BOTTOM_PADDING / Global.BLOCK_SIZE) - 1
        self._min_col = - math.ceil(Global.LEFT_PADDING / Global.BLOCK_SIZE)
        self._max_col = Global.GRID_COL + math.ceil(Global.RIGHT_PADDING / Global.BLOCK_SIZE) - 1

        self.move_speed: int = 20
        self.move_timer = Util.timer(0.666 / self.move_speed)

    def start(self) -> None:
        self.move_timer.start()

    def pause(self) -> None:
        self.move_timer.pause()

    def _add_snake(self) -> None:
        new_y = self._min_row  # make sure snakes appear from the top of screen
        regenerate_times = 0
        while True:
            # make sure snakes appear from the left edge and right edge of screen
            new_x = random.randint(self._min_col, self._max_col - 1)
            length = random.randint(5, 25)
            regenerate = False
            for little_snake in self._little_fresh_snakes:
                if -1 <= little_snake.x[0] - new_x <= 1:
                    regenerate = True
                    break
            if regenerate and regenerate_times <= 1:
                regenerate_times += 1
                continue
            self._little_fresh_snakes.append(
                LittleSnake(new_x, new_y, length, self.move_speed, self._grid)
            )
            break

    def update(self) -> None:
        if not self.move_timer.arrived:
            return
        if random.randint(0, 2) == 0:
            self._add_snake()

        for i in range(len(self._little_fresh_snakes) - 1, -1, -1):
            if self._little_fresh_snakes[i].y[-1] > 5:
                self._little_on_screen_snakes.append(self._little_fresh_snakes.pop(i))
            else:
                self._little_fresh_snakes[i].walk(teleport=False, reg_grid=False)

        for i in range(len(self._little_on_screen_snakes) - 1, -1, -1):
            if self._little_on_screen_snakes[i].y[-1] > self._max_row:
                # make sure the snake is removed only after the tail leaves the screen
                self._little_on_screen_snakes.pop(i)
            else:
                self._little_on_screen_snakes[i].walk(teleport=False, reg_grid=False)

    def draw(self, surface: pygame.Surface) -> None:
        for little_snake in self._little_fresh_snakes:
            little_snake.draw(surface)
        for little_snake in self._little_on_screen_snakes:
            little_snake.draw(surface)
        surface.blit(Util.gaussian_blur(surface, 21), (0, 0))
