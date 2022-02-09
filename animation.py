import pygame
import random
import game
from settings import Global
from snake import Snake
from event_manager import EventManager
from util import Util


class LittleSnake(Snake):
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game', x, y, length, move_speed):
        super().__init__(parent_surface, parent_game)
        self.direction = "down"
        self.length = length
        self.x = [x] * self.length
        self.y = [y * Global.BLOCK_SIZE - Global.BLOCK_SIZE * (i + 1) for i in range(self.length)]
        self.move_speed = move_speed


class AnimationManager:
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        self._parent_surface = parent_surface
        self._parent_game = parent_game
        self.little_snakes: list[Snake] = []
        self.move_speed = 20
        self.event_timer = Util.generate_user_event_id()

        pygame.time.set_timer(self.event_timer, int(1000 / (1.5 * self.move_speed)))

    def _add_snake(self):
        new_x = random.randint(0, (Global.GRID_COL - 1)) * Global.BLOCK_SIZE
        new_y = 0
        length = random.randint(3, 15)
        self.little_snakes.append(
            LittleSnake(self._parent_surface, self._parent_game, new_x, new_y, length, self.move_speed)
        )

    def update(self, _event_manager: EventManager):
        if not _event_manager.match_event_type(self.event_timer):
            return
        self._add_snake()
        for i in range(len(self.little_snakes) - 1, -1, -1):
            if self.little_snakes[i].y[-1] >= Global.SCREEN_SIZE[1]:
                self.little_snakes.pop(i)
            else:
                self.little_snakes[i].walk(teleport=False)

    def render(self):
        for little_snake in self.little_snakes:
            little_snake.draw()
        self._parent_surface.blit(Util.gaussian_blur(self._parent_surface, 21), (0, 0))
