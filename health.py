import pygame
# from game import Game
from settings import *


class Health:
    def __init__(self, parent_surface, parent_game):
        self.parent_surface = parent_surface
        self.parent_game = parent_game
        self.image = pygame.image.load("resources/imgs/heart.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (Global.UI_SCALE, Global.UI_SCALE))
        self.value = Global.INIT_HEALTH

    def draw(self):
        for i in range(self.value):
            self.parent_surface.blit(self.image,
                                     (i * self.image.get_width(),
                                      self.parent_surface.get_height() - self.image.get_height()))

    def increase_health(self, _value):
        # filter: [0, MAX_HEALTH]
        self.value = max(min(Global.MAX_HEALTH, self.value + _value), 0)

    def reset(self):
        self.value = Global.INIT_HEALTH


class Hungry:
    def __init__(self, parent_surface, parent_game):
        self.parent_surface = parent_surface
        self.parent_game = parent_game
        self.image = pygame.image.load("resources/imgs/hunger_bigger.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (Global.UI_SCALE, Global.UI_SCALE))
        self.hungry_step_count = 0

        self.__value = 0

    def draw(self):
        for i in range(self.get_satiety()):
            self.parent_surface.blit(self.image,
                                     (self.parent_surface.get_width() - (i + 1) * self.image.get_width(),
                                      self.parent_surface.get_height() - self.image.get_height()))

    def get_satiety(self):
        # interval: [0, INIT_SATIETY]
        return Global.INIT_SATIETY - self.__value

    def get_hungry_value(self):
        # interval: [0, INIT_SATIETY]
        # duplicated to get_satiety, do not use if necessary
        return self.__value

    def increase_satiety(self, _value):
        # filter: [0, MAX_SATIETY]
        # decrease hungry value to increase satiety
        self.__value = max(min(Global.MAX_SATIETY, self.__value - _value), 0)

        # reset hungry step count after satiety actually increased
        if _value > 0:
            self.hungry_step_count = 0

    def reset(self):
        self.hungry_step_count = 0
        self.__value = 0
