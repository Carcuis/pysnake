import random

import pygame

from event import EventManager
from settings import Global
from snake import Snake
from util import Util


class LittleSnake(Snake):
    def __init__(self, x: int, y: int, length: int, move_speed: int) -> None:
        super().__init__()
        self.direction = "down"
        self.length = length
        self.x = [x] * self.length
        self.y = [y * Global.BLOCK_SIZE - Global.BLOCK_SIZE * (i + 1) for i in range(self.length)]
        self.move_speed = move_speed


class AnimationManager:
    def __init__(self) -> None:
        self._little_fresh_snakes: list[Snake] = []
        self._little_on_screen_snakes: list[Snake] = []
        self.move_speed: int = 20
        self.event_timer = Util.generate_user_event_id(timer=True)

        pygame.time.set_timer(self.event_timer, int(1000 / (1.5 * self.move_speed)))

    def _add_snake(self) -> None:
        new_y = 0
        while True:
            new_x = random.randint(0, (Global.GRID_COL - 1)) * Global.BLOCK_SIZE
            length = random.randint(5, 25)
            regenerate = False
            regenerate_times = 0
            for little_snake in self._little_fresh_snakes:
                if - Global.BLOCK_SIZE <= little_snake.x[0] - new_x <= Global.BLOCK_SIZE:
                    regenerate = True
                    break
            if regenerate and regenerate_times <= 3:
                regenerate_times += 1
                continue
            self._little_fresh_snakes.append(
                LittleSnake(new_x, new_y, length, self.move_speed)
            )
            break

    def update(self) -> None:
        if not EventManager.match_event_type(self.event_timer):
            return
        if random.randint(0, 2) == 0:
            self._add_snake()

        for i in range(len(self._little_fresh_snakes) - 1, -1, -1):
            if self._little_fresh_snakes[i].y[-1] > 5 * Global.BLOCK_SIZE:
                self._little_on_screen_snakes.append(self._little_fresh_snakes.pop(i))
            else:
                self._little_fresh_snakes[i].walk(teleport=False)

        for i in range(len(self._little_on_screen_snakes) - 1, -1, -1):
            if self._little_on_screen_snakes[i].y[-1] >= Global.SCREEN_SIZE[1]:
                self._little_on_screen_snakes.pop(i)
            else:
                self._little_on_screen_snakes[i].walk(teleport=False)

    def draw(self, surface: pygame.Surface) -> None:
        for little_snake in self._little_fresh_snakes:
            little_snake.draw(surface)
        for little_snake in self._little_on_screen_snakes:
            little_snake.draw(surface)
        surface.blit(Util.gaussian_blur(surface, 21), (0, 0))
