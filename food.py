import pygame
import random
import game
from settings import Global


class FoodManager:
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        self._parent_surface = parent_surface
        self._parent_game = parent_game

        self.apple = Apple(self._parent_surface, self._parent_game)
        self.beef = Beef(self._parent_surface, self._parent_game)
        self.iron = Iron(self._parent_surface, self._parent_game)
        self.gold = Gold(self._parent_surface, self._parent_game)
        self.slimeball = SlimeBall(self._parent_surface, self._parent_game)
        self.heart = Heart(self._parent_surface, self._parent_game)

        self.food_list = (self.apple, self.beef, self.iron, self.gold, self.slimeball, self.heart)

    def draw(self):
        for food in self.food_list:
            food.draw()

    def reset(self):
        for food in self.food_list:
            food.x.clear()
            food.y.clear()
            food.count = 0


class FoodBase:
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        self.image = None
        self._parent_surface = parent_surface
        self._parent_game = parent_game
        self.count = 0
        self.x = []
        self.y = []
        self.add_satiety = 0
        self.toxic_level = 0
        self.add_score = 0
        self.increase_speed = 0
        self.increase_length = 0

    def draw(self):
        if self.count > 0:
            for i in range(self.count):
                self._parent_surface.blit(self.image, (self.x[i], self.y[i]))

    def update(self, index=None):
        # delete specific food after is eaten
        if index is not None:
            del self.x[index]
            del self.y[index]
            self.count -= 1

        while True:
            temp_x = random.randrange(
                Global.LEFT_PADDING, Global.SCREEN_SIZE[0] - Global.RIGHT_PADDING, Global.BLOCK_SIZE
            )
            temp_y = random.randrange(
                Global.TOP_PADDING, Global.SCREEN_SIZE[1] - Global.BOTTOM_PADDING, Global.BLOCK_SIZE
            )

            overlap = False

            # overlap with snake
            for i in range(self._parent_game.snake.length):
                if temp_x == self._parent_game.snake.x[i] and temp_y == self._parent_game.snake.y[i]:
                    overlap = True
                    break
            if overlap:
                continue

            # overlap with other food
            for food in self._parent_game.food_manager.food_list:
                if food.count > 0:
                    for i in range(food.count):
                        if temp_x == food.x[i] and temp_y == food.y[i]:
                            overlap = True
                            break
                if overlap:
                    break
            if overlap:
                continue

            # overlap with wall
            if (temp_x, temp_y) in self._parent_game.wall.coords:
                continue

            self.x.append(temp_x)
            self.y.append(temp_y)
            self.count += 1

            # add food at random until count >= 3
            if self.count < 3 and random.randint(1, 4) == 1:
                continue

            break


class Apple(FoodBase):
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        super().__init__(parent_surface, parent_game)
        self.image = pygame.image.load("resources/img/apple_bigger.png").convert()
        self.image = pygame.transform.scale(self.image, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.add_satiety = 1
        self.toxic_level = 0
        self.add_score = 0
        self.increase_speed = 0
        self.increase_length = 1


class Beef(FoodBase):
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        super().__init__(parent_surface, parent_game)
        self.image = pygame.image.load("resources/img/beef_bigger.png").convert()
        self.image = pygame.transform.scale(self.image, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.add_satiety = 2
        self.toxic_level = 0
        self.add_score = 0
        self.increase_speed = 0
        self.increase_length = 2


class Iron(FoodBase):
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        super().__init__(parent_surface, parent_game)
        self.image = pygame.image.load("resources/img/iron_block.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.add_satiety = 1
        self.toxic_level = 0
        self.add_score = 2
        self.increase_speed = 0
        self.increase_length = 1


class Gold(FoodBase):
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        super().__init__(parent_surface, parent_game)
        self.image = pygame.image.load("resources/img/gold_bigger.png").convert()
        self.image = pygame.transform.scale(self.image, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.add_satiety = 2
        self.toxic_level = 0
        self.add_score = 4
        self.increase_speed = 1
        self.increase_length = 1


class SlimeBall(FoodBase):
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        super().__init__(parent_surface, parent_game)
        self.image = pygame.image.load("resources/img/slimeball_bigger.png").convert()
        self.image = pygame.transform.scale(self.image, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.add_satiety = 1
        self.toxic_level = 1
        self.add_score = 1
        self.increase_speed = -1
        self.increase_length = 1


class Heart(FoodBase):
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        super().__init__(parent_surface, parent_game)
        self.image = pygame.image.load("resources/img/heart.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (Global.BLOCK_SIZE, Global.BLOCK_SIZE))
        self.add_satiety = 1
        self.toxic_level = -1
        self.add_score = 1
        self.increase_speed = 0
        self.increase_length = 1
