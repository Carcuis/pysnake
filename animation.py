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
        self._little_fresh_snakes: list[Snake] = []
        self._little_on_screen_snakes: list[Snake] = []
        self.move_speed = 20
        self.event_timer = Util.generate_user_event_id()

        pygame.time.set_timer(self.event_timer, int(1000 / (1.5 * self.move_speed)))

    def _add_snake(self):
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
                LittleSnake(self._parent_surface, self._parent_game, new_x, new_y, length, self.move_speed)
            )
            break

    def update(self, _event_manager: EventManager):
        if not _event_manager.match_event_type(self.event_timer):
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

    def render(self):
        for little_snake in self._little_fresh_snakes:
            little_snake.draw()
        for little_snake in self._little_on_screen_snakes:
            little_snake.draw()
        self._parent_surface.blit(Util.gaussian_blur(self._parent_surface, 21), (0, 0))
