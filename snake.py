import pygame

from health import Health, Hungry
from settings import Global


class Snake:
    def __init__(self) -> None:
        self.head_block = pygame.transform.scale(
            pygame.image.load("resources/img/yellow-fdd926-10x10.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.body_block = pygame.transform.scale(
            pygame.image.load("resources/img/green-23d12f-10x10.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )

        self.health: Health = Health()
        self.hungry: Hungry = Hungry()
        self.init_length = Global.INIT_LENGTH
        self.length = self.init_length
        self.x = [10 * Global.BLOCK_SIZE + Global.BLOCK_SIZE * (self.length - i - 1) for i in range(self.length)]
        self.y = [2 * Global.BLOCK_SIZE] * self.length

        self.move_speed: int = Global.INIT_SPEED
        self.speed_changed: bool = False
        self.direction: str = "right"
        self.direction_lock: bool = False
        self.direction_buffer: str = ""

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.head_block, (self.x[0], self.y[0]))
        for i in range(1, self.length):
            surface.blit(self.body_block, (self.x[i], self.y[i]))

    def change_direction(self, direction: str) -> None:
        if self.direction_lock:
            self.direction_buffer = direction
            return

        if self.direction == direction:
            return

        self.direction_lock = True
        if direction == "left" and self.direction != "right":
            self.direction = "left"
        if direction == "right" and self.direction != "left":
            self.direction = "right"
        if direction == "up" and self.direction != "down":
            self.direction = "up"
        if direction == "down" and self.direction != "up":
            self.direction = "down"

    def walk(self, teleport=True) -> None:
        # move body from tail to neck
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # move head
        step = Global.BLOCK_SIZE
        if self.direction == "left":
            self.x[0] -= step
        elif self.direction == "right":
            self.x[0] += step
        elif self.direction == "up":
            self.y[0] -= step
        elif self.direction == "down":
            self.y[0] += step

        if teleport:
            # teleport head if is over border after movement
            over_border, border_position = self.head_over_border()
            if over_border:
                self.teleport(border_position)

        self.direction_lock = False

        # execute buffer mode changing direction if buffer mode is set
        if self.direction_buffer != "":
            self.change_direction(self.direction_buffer)
            self.direction_buffer = ""

        self.hungry.hungry_step_count += 1

    def head_over_border(self) -> tuple[bool, str]:
        """
        :return: (bool: over_border, str: border_position)
        """
        if self.x[0] < Global.LEFT_PADDING:
            return True, "left"
        if self.x[0] >= Global.SCREEN_SIZE[0] - Global.RIGHT_PADDING:
            return True, "right"
        if self.y[0] < Global.TOP_PADDING:
            return True, "top"
        if self.y[0] >= Global.SCREEN_SIZE[1] - Global.BOTTOM_PADDING:
            return True, "bottom"
        return False, "none"

    def teleport(self, _from: str) -> None:
        if _from == "left":
            # to right
            self.x[0] = Global.SCREEN_SIZE[0] - Global.BLOCK_SIZE - Global.RIGHT_PADDING
        elif _from == "right":
            # to left
            self.x[0] = Global.LEFT_PADDING
        elif _from == "top":
            # to bottom
            self.y[0] = Global.SCREEN_SIZE[1] - Global.BLOCK_SIZE - Global.BOTTOM_PADDING
        elif _from == "bottom":
            # to top
            self.y[0] = Global.TOP_PADDING
        else:
            return

    def increase_length(self, length: int) -> None:
        if length < 0:
            return
        self.length += length
        for _ in range(length):
            self.x.append(self.x[-1])
            self.y.append(self.y[-1])

    def increase_speed(self, speed: int) -> None:
        # filter: [MIN_SPEED, MAX_SPEED]
        self.move_speed = min(max(Global.MIN_SPEED, self.move_speed + speed), Global.MAX_SPEED)
        self.speed_changed = True

    def reset(self) -> None:
        self.init_length = Global.INIT_LENGTH
        self.length = self.init_length
        self.x = [10 * Global.BLOCK_SIZE + Global.BLOCK_SIZE * (self.length - i - 1) for i in range(self.length)]
        self.y = [2 * Global.BLOCK_SIZE] * self.length

        self.move_speed = Global.INIT_SPEED
        self.speed_changed = True
        self.direction = "right"
        self.direction_lock = False
        self.direction_buffer = ""
