import pygame
from pygame.locals import *


class EventManager:
    def __init__(self, parent_game):
        from game import Game
        self._parent_game: Game = parent_game
        self.event_list = []
        self.keys_pressed = dict()
        self.mouse_button_status = tuple()
        self.mouse_pos = (-1, -1)

    def get_event(self):
        """
        Execute at the beginning of each cycle of every loop.
        """
        self.event_list = pygame.event.get()
        # for i in self.event_list:
        #     print(i)
        if self.match_event_type(QUIT):
            """ always check exit """
            self._parent_game.quit_game()
        self.keys_pressed = pygame.key.get_pressed()
        self.mouse_button_status = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()

    def match_event_type(self, _type):
        for event in self.event_list:
            if event.type == _type:
                return True
        return False

    def check_key_or_button(self, event_type, attribute):
        """
        check if mouse button or keyboard key up or down
        :param event_type: mouse: MOUSEBUTTONDOWN or MOUSEBUTTONUP
                           key: KEYDOWN or KEYUP
        :param attribute: (set or value) mouse: 1->left 2->middle 3->right 4->wheel_up 5->wheel_down / key
        :return: bool: whether match event_type and button
        """
        for event in self.event_list:
            if event.type == event_type:
                if event_type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN):
                    if isinstance(attribute, set):
                        return event.button in attribute
                    return event.button == attribute
                elif event_type in (KEYUP, KEYDOWN):
                    if isinstance(attribute, set):
                        return event.key in attribute
                    return event.key == attribute
        return False
