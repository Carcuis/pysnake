import enum

import pygame

from grid import Grid
from health import Health, Hungry
from settings import Global


@enum.unique
class Direction(enum.Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Snake:
    def __init__(self, grid: Grid) -> None:
        self.head_block = pygame.transform.scale(
            pygame.image.load("resources/img/yellow-fdd926-10x10.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.body_block = pygame.transform.scale(
            pygame.image.load("resources/img/green-23d12f-10x10.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )

        self._grid: Grid = grid
        self.health: Health = Health()
        self.hungry: Hungry = Hungry()
        self.init_length: int = Global.INIT_LENGTH
        self.length: int = self.init_length
        self.x = [Global.INIT_POS[0] + (self.length - i - 1) for i in range(self.length)]
        self.y = [Global.INIT_POS[1]] * self.length
        for i in range(self.length):
            self._grid.set_type(self.x[i], self.y[i], 'body')

        self.move_speed: int = Global.INIT_SPEED
        self.speed_changed: bool = False
        self.direction: Direction = Direction.RIGHT
        self.direction_buffer: Direction = Direction.NONE
        self.changing_direction: bool = False

    def reset(self) -> None:
        self.length = self.init_length
        self.x = [Global.INIT_POS[0] + (self.length - i - 1) for i in range(self.length)]
        self.y = [Global.INIT_POS[1]] * self.length
        for i in range(self.length):
            self._grid.set_type(self.x[i], self.y[i], 'body')

        self.move_speed = Global.INIT_SPEED
        self.speed_changed = False
        self.direction = Direction.RIGHT
        self.direction_buffer = Direction.NONE
        self.changing_direction = False

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(
            self.head_block,
            (self.x[0] * Global.BLOCK_SIZE + Global.LEFT_PADDING,
             self.y[0] * Global.BLOCK_SIZE + Global.TOP_PADDING)
        )
        for i in range(1, self.length):
            surface.blit(
                self.body_block,
                (self.x[i] * Global.BLOCK_SIZE + Global.LEFT_PADDING,
                 self.y[i] * Global.BLOCK_SIZE + Global.TOP_PADDING)
            )

    def change_direction(self, target_direction: Direction) -> bool:
        if target_direction not in Direction or target_direction == Direction.NONE:
            raise ValueError(f"Invalid direction: {target_direction}")
        if self.direction == target_direction:
            return False
        if {target_direction, self.direction} == {Direction.LEFT, Direction.RIGHT} or \
                {target_direction, self.direction} == {Direction.UP, Direction.DOWN}:
            # prevent 180-degree turns
            return False
        if self.changing_direction:
            # push into buffer when direction is locked
            self.direction_buffer = target_direction
            return False

        self.changing_direction = True  # lock direction
        self.direction = target_direction  # finally change direction
        return True

    def walk(self, teleport=True, reg_grid=True) -> None:
        # save tail
        old_tail_x, old_tail_y = self.x[-1], self.y[-1]

        # move body from tail to neck
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # move head
        if self.direction == Direction.LEFT:
            self.x[0] -= 1
        elif self.direction == Direction.RIGHT:
            self.x[0] += 1
        elif self.direction == Direction.UP:
            self.y[0] -= 1
        elif self.direction == Direction.DOWN:
            self.y[0] += 1

        if teleport:
            # teleport head if is over border after movement
            if self.x[0] < 0:
                self.x[0] = Global.GRID_COL - 1
            elif self.x[0] >= Global.GRID_COL:
                self.x[0] = 0
            if self.y[0] < 0:
                self.y[0] = Global.GRID_ROW - 1
            elif self.y[0] >= Global.GRID_ROW:
                self.y[0] = 0

        if reg_grid:
            # register body type of new head to grid cell
            self._grid.set_type(self.x[0], self.y[0], 'body')
            if (old_tail_x, old_tail_y) not in zip(self.x, self.y):
                # unset old tail's body type from the grid cell if it does not collide with body
                self._grid.clear_type(old_tail_x, old_tail_y, 'body')

        self.changing_direction = False  # unlock direction
        self.hungry.hungry_step_count += 1

        if self.direction_buffer != Direction.NONE:
            # pop buffer
            self.change_direction(self.direction_buffer)
            self.direction_buffer = Direction.NONE

    def increase_length(self, length: int) -> bool:
        if length < 0:
            return False
        self.length += length
        for _ in range(length):
            self.x.append(self.x[-1])
            self.y.append(self.y[-1])
        return True

    def increase_speed(self, speed: int) -> None:
        # filter: [MIN_SPEED, MAX_SPEED]
        self.move_speed = min(max(Global.MIN_SPEED, self.move_speed + speed), Global.MAX_SPEED)
        self.speed_changed = True
