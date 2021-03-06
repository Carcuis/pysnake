import pygame
import time
import cv2
import os
import json


class Util:
    user_event_count: int = 0

    @classmethod
    def generate_user_event_id(cls):
        new_id = cls.user_event_count + pygame.USEREVENT
        cls.user_event_count += 1
        return new_id

    @staticmethod
    def scale_blur(surface, value):
        """
        Blur the given surface by the given 'value'.
        :param surface: input surface
        :param value: Interval: [1, +inf).  Value 1 = no blur.
        :return: produced surface
        """
        if value < 1.0:
            raise ValueError("Arg 'value' must be greater than 1.0, passed in value is %s" % value)
        scale = 1.0 / float(value)
        surf_size = surface.get_size()
        scale_size = (int(surf_size[0] * scale), int(surf_size[1] * scale))
        surf = pygame.transform.smoothscale(surface, scale_size)
        surf = pygame.transform.smoothscale(surf, surf_size)
        return surf

    @staticmethod
    def gaussian_blur(surface, kernel_size, sigma_x=0):
        """
        Blur surface using gaussian filter.
        :param surface: input surface
        :param kernel_size: gaussian filter kernel size, must be odd int
        :param sigma_x: gaussian filter sigma x
        :return: produced surface
        """
        surface = pygame.surfarray.array3d(surface)
        surface = cv2.cvtColor(cv2.transpose(surface), cv2.COLOR_RGB2BGR)
        surface = cv2.GaussianBlur(surface, (kernel_size, kernel_size), sigma_x)
        surface = cv2.transpose(cv2.cvtColor(surface, cv2.COLOR_BGR2RGB))
        surface = pygame.surfarray.make_surface(surface)
        return surface

    @staticmethod
    def update_screen():
        """
        Actually draw surface to screen.
        """
        pygame.display.flip()

    @staticmethod
    def load_data_from_json_file(file_name):
        """
        Load dict data from json file.
        :param file_name: json file name
        :return: data: dict()
        """
        # create if file not found
        open(file_name, 'a').close()

        with open(file_name, mode="r") as fp:
            empty = False
            if os.path.getsize(file_name) == 0:
                empty = True
            if not empty:
                return json.load(fp)
            return dict()

    @staticmethod
    def write_data_to_json_file(file_name, data):
        """
        Write data to json file.
        :param file_name: json file name
        :param data: data to write, must be dict
        """
        with open(file_name, mode="w") as fp:
            json.dump(data, fp, indent=4)

    @staticmethod
    def measure_time():
        def wraps(func):
            def measure(*args, **kwargs):
                start = time.perf_counter_ns()
                res = func(*args, **kwargs)
                end = time.perf_counter_ns()
                print(f"Function {func.__name__} used {(end - start) / 1e6} ms.")
                return res
            return measure
        return wraps
