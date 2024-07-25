import pygame

from settings import Global


class Health:
    def __init__(self) -> None:
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/heart.png").convert_alpha(),
            (Global.UI_SCALE, Global.UI_SCALE)
        )
        self.value: int = Global.INIT_HEALTH

    def reset(self) -> None:
        self.value = Global.INIT_HEALTH

    def draw(self, surface: pygame.Surface) -> None:
        for i in range(self.value):
            surface.blit(
                self.image,
                (i * self.image.get_width(), surface.get_height() - self.image.get_height())
            )

    def increase(self, _value: int) -> None:
        # filter: [0, MAX_HEALTH]
        self.value = max(min(Global.MAX_HEALTH, self.value + _value), 0)


class Hungry:
    def __init__(self) -> None:
        self.image = pygame.transform.scale(
            pygame.image.load("resources/img/hunger_bigger.png").convert_alpha(),
            (Global.UI_SCALE, Global.UI_SCALE)
        )
        self.hungry_step_count: int = 0
        self._value: int = 0

    def reset(self) -> None:
        self.hungry_step_count = 0
        self._value = 0

    def draw(self, surface: pygame.Surface) -> None:
        for i in range(self.get_satiety()):
            surface.blit(
                self.image,
                (surface.get_width() - (i + 1) * self.image.get_width(),
                 surface.get_height() - self.image.get_height())
            )

    def get_satiety(self) -> int:
        # interval: [0, INIT_SATIETY]
        return Global.INIT_SATIETY - self._value

    def get_hungry_value(self) -> int:
        # interval: [0, INIT_SATIETY]
        # duplicated to get_satiety, do not use if necessary
        return self._value

    def increase_satiety(self, value: int) -> None:
        # filter: [0, MAX_SATIETY]
        # decrease hungry value to increase satiety
        self._value = max(min(Global.MAX_SATIETY, self._value - value), 0)

        # reset hungry step count after satiety actually increased
        if value > 0:
            self.hungry_step_count = 0
