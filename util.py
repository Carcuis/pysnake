import json
import os
import sys
import time
from typing import Callable, NoReturn

import cv2
import pygame


class Util:
    user_event_count: int = 0

    @classmethod
    def generate_user_event_id(cls) -> int:
        new_id = cls.user_event_count + pygame.USEREVENT
        cls.user_event_count += 1
        return new_id

    @staticmethod
    def scale_blur(surface: pygame.Surface, value: float) -> pygame.Surface:
        """
        Blur the given surface by the given 'value'.
        :param surface: input surface
        :param value: Interval: [1, +inf).  Value 1 = no blur.
        :return: produced surface
        """
        if value < 1.0:
            raise ValueError("Arg 'value' must be greater than 1.0, passed in value is %s" % value)
        scale = 1.0 / value
        surf_size = surface.get_size()
        scale_size = (surf_size[0] * scale, surf_size[1] * scale)
        surf = pygame.transform.smoothscale(surface, scale_size)
        surf = pygame.transform.smoothscale(surf, surf_size)
        return surf

    @staticmethod
    def gaussian_blur(surface: pygame.Surface, kernel_size: int, sigma_x: int = 0) -> pygame.Surface:
        """
        Blur surface using gaussian filter.
        :param surface: input surface
        :param kernel_size: gaussian filter kernel size, must be odd int
        :param sigma_x: gaussian filter sigma x
        :return: produced surface
        """
        array = pygame.surfarray.array3d(surface)
        array = cv2.cvtColor(cv2.transpose(array), cv2.COLOR_RGB2BGR)
        array = cv2.GaussianBlur(array, (kernel_size, kernel_size), sigma_x)
        array = cv2.transpose(cv2.cvtColor(array, cv2.COLOR_BGR2RGB))
        surface = pygame.surfarray.make_surface(array)
        return surface

    @staticmethod
    def update_screen() -> None:
        """
        Actually draw surface to screen.
        """
        pygame.display.flip()

    @staticmethod
    def load_data_from_json_file(file_name: str) -> dict:
        """
        Load dict data from json file.
        :param file_name: json file name
        :return: data: dict
        """
        # create one if file not found
        open(file_name, 'a').close()

        with open(file_name, mode="r") as fp:
            if os.path.getsize(file_name) == 0:
                # file empty
                return dict()
            return json.load(fp)

    @staticmethod
    def write_data_to_json_file(file_name: str, data: dict) -> None:
        """
        Write data to json file.
        :param file_name: json file name
        :param data: data to write
        """
        with open(file_name, mode="w") as fp:
            json.dump(data, fp, indent=4)

    @staticmethod
    def measure_time(func: Callable):
        def wrapper(*args, **kwargs):
            start = time.perf_counter_ns()
            res = func(*args, **kwargs)
            end = time.perf_counter_ns()
            print(f"Function {func.__name__} used {(end - start) / 1e6} ms.")
            return res
        return wrapper

    @staticmethod
    def quit_game() -> NoReturn:
        print("\033[1;36mBye.\033[0m")
        sys.exit()
