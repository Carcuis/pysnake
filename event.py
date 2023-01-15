import pygame

from util import Util


class EventManager:
    event_list: list[pygame.event.Event] = []
    keys_pressed: tuple = ()
    mouse_button_status: tuple = ()
    mouse_pos = (-1, -1)

    @classmethod
    def get_event(cls) -> None:
        """
        Execute at the beginning of each cycle of every loop.
        """
        cls.event_list = pygame.event.get()
        # cls.print_event(ignore_timer=True)
        if cls.match_event_type(pygame.QUIT):
            """ always check exit """
            Util.quit_game()
        cls.keys_pressed = pygame.key.get_pressed()
        cls.mouse_button_status = pygame.mouse.get_pressed()
        cls.mouse_pos = pygame.mouse.get_pos()

    @classmethod
    def match_event_type(cls, _type) -> bool:
        for event in cls.event_list:
            if event.type == _type:
                return True
        return False

    @classmethod
    def check_key_or_button(cls, event_type, attribute) -> bool:
        """
        check if mouse button or keyboard key up or down
        :param event_type: mouse: MOUSEBUTTONDOWN or MOUSEBUTTONUP
                           key: KEYDOWN or KEYUP
        :param attribute: (set or value) mouse: 1->left 2->middle 3->right 4->wheel_up 5->wheel_down / key
        :return: bool: whether match event_type and button
        """
        for event in cls.event_list:
            if event.type == event_type:
                if event_type in (pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                    if isinstance(attribute, set):
                        return event.button in attribute
                    return event.button == attribute
                elif event_type in (pygame.KEYUP, pygame.KEYDOWN):
                    if isinstance(attribute, set):
                        return event.key in attribute
                    return event.key == attribute
        return False

    @classmethod
    def print_event(cls, ignore_timer=False) -> None:
        for event in cls.event_list:
            if ignore_timer:
                if event.type in Util.user_timer_list:
                    continue
            print(event)
