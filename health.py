import pygame
import game
from settings import Global


class Health:
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        self._parent_surface = parent_surface
        self._parent_game = parent_game
        self.image = pygame.image.load("resources/img/heart.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (Global.UI_SCALE, Global.UI_SCALE))
        self.value = Global.INIT_HEALTH

    def draw(self):
        for i in range(self.value):
            self._parent_surface.blit(
                self.image,
                (i * self.image.get_width(), self._parent_surface.get_height() - self.image.get_height())
            )

    def increase_health(self, _value):
        # filter: [0, MAX_HEALTH]
        self.value = max(min(Global.MAX_HEALTH, self.value + _value), 0)

    def reset(self):
        self.value = Global.INIT_HEALTH


class Hungry:
    def __init__(self, parent_surface: pygame.Surface, parent_game: 'game.Game'):
        self._parent_surface = parent_surface
        self._parent_game = parent_game
        self.image = pygame.image.load("resources/img/hunger_bigger.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (Global.UI_SCALE, Global.UI_SCALE))
        self.hungry_step_count = 0

        self._value = 0

    def draw(self):
        for i in range(self.get_satiety()):
            self._parent_surface.blit(
                self.image,
                (self._parent_surface.get_width() - (i + 1) * self.image.get_width(),
                 self._parent_surface.get_height() - self.image.get_height())
            )

    def get_satiety(self):
        # interval: [0, INIT_SATIETY]
        return Global.INIT_SATIETY - self._value

    def get_hungry_value(self):
        # interval: [0, INIT_SATIETY]
        # duplicated to get_satiety, do not use if necessary
        return self._value

    def increase_satiety(self, __value):
        # filter: [0, MAX_SATIETY]
        # decrease hungry value to increase satiety
        self._value = max(min(Global.MAX_SATIETY, self._value - __value), 0)

        # reset hungry step count after satiety actually increased
        if __value > 0:
            self.hungry_step_count = 0

    def reset(self):
        self.hungry_step_count = 0
        self._value = 0
