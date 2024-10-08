import random

import pygame

from grid import Grid
from settings import Global


class FoodManager:
    def __init__(self, grid: Grid, surface: pygame.Surface) -> None:
        self._grid: Grid = grid
        self._surface: pygame.Surface = surface

        self.apple = Apple()
        if not Global.WITH_AI:
            # full list of food
            self.beef = Beef()
            self.iron = Iron()
            self.gold = Gold()
            self.slimeball = SlimeBall()
            self.heart = Heart()
            self.food_list = (self.apple, self.beef, self.iron, self.gold, self.slimeball, self.heart)
        else:
            # only has apple, for ai-training
            self.food_list = (self.apple,)

        self.update_all()

    def reset(self) -> None:
        for food in self.food_list:
            food.x.clear()
            food.y.clear()
            food.count = 0
            food.update(self._grid, self._surface)

    def draw(self) -> None:
        for food in self.food_list:
            food.draw(self._surface)

    def update_all(self) -> None:
        for food in self.food_list:
            food.update(self._grid, self._surface)


class FoodBase:
    def __init__(self) -> None:
        self.name: str = ""
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/red-f01414-10x10.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.count: int = 0
        self.x: list[int] = []
        self.y: list[int] = []
        self.add_satiety: int = 0
        self.toxic_level: int = 0
        self.add_score: int = 0
        self.increase_speed: int = 0
        self.increase_length: int = 0

    def draw(self, surface: pygame.Surface) -> None:
        if self.image is None:
            raise TypeError("Food image is None.")
        for i in range(self.count):
            surface.blit(
                self.image,
                (self.x[i] * Global.BLOCK_SIZE + Global.LEFT_PADDING,
                 self.y[i] * Global.BLOCK_SIZE + Global.TOP_PADDING)
            )

    def update(self, grid: Grid, surface: pygame.Surface, index=None) -> None:
        # delete specific food after is eaten
        if index is not None:
            grid.clear_type(self.x[index], self.y[index], self.name)
            del self.x[index]
            del self.y[index]
            self.count -= 1

        while True:
            if grid.get_empty_count() <= 0:
                break

            new_x = random.randint(0, Global.GRID_COL - 1)
            new_y = random.randint(0, Global.GRID_ROW - 1)

            if not grid.is_empty(new_x, new_y):
                continue

            grid.set_type(new_x, new_y, self.name)
            self.x.append(new_x)
            self.y.append(new_y)
            self.count += 1
            surface.blit(
                self.image,
                (new_x * Global.BLOCK_SIZE + Global.LEFT_PADDING,
                 new_y * Global.BLOCK_SIZE + Global.TOP_PADDING)
            )

            # add food at random until count >= max_count
            if self.count < Global.FOOD_MAX_COUNT_PER_KIND and random.randint(1, 4) == 1:
                continue

            break


class Apple(FoodBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "apple"
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/apple_bigger.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.add_satiety = 1
        self.toxic_level = 0
        self.add_score = 0
        self.increase_speed = 0
        self.increase_length = 1


class Beef(FoodBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "beef"
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/beef_bigger.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.add_satiety = 2
        self.toxic_level = 0
        self.add_score = 0
        self.increase_speed = 0
        self.increase_length = 2


class Iron(FoodBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "iron"
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/iron_block.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.add_satiety = 1
        self.toxic_level = 0
        self.add_score = 2
        self.increase_speed = 0
        self.increase_length = 1


class Gold(FoodBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "gold"
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/gold_bigger.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.add_satiety = 2
        self.toxic_level = 0
        self.add_score = 4
        self.increase_speed = 1
        self.increase_length = 1


class SlimeBall(FoodBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "slimeball"
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/slimeball_bigger.png").convert(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.add_satiety = 1
        self.toxic_level = 1
        self.add_score = 1
        self.increase_speed = -1
        self.increase_length = 1


class Heart(FoodBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "heart"
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/heart.png").convert_alpha(),
            (Global.BLOCK_SIZE, Global.BLOCK_SIZE)
        )
        self.add_satiety = 1
        self.toxic_level = -1
        self.add_score = 1
        self.increase_speed = 0
        self.increase_length = 1
