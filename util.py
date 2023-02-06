import json
import os
import sys
import time
from threading import Thread, Event
from typing import Callable, NoReturn

import cv2
import pygame


class RepeatedTimer(Thread):
    """ (Modified from threading.Timer.)
    Call a function repeatedly after a specified number of seconds:
            t = RepeatedTimer(30.0, f, args=None, kwargs=None)
            t.start()  t.stop()  # start and stop
            t.pause()  t.resume()  # pause and resume
    """

    def __init__(self, interval: float, function: Callable, args=None, kwargs=None) -> None:
        Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.function = function
        self.args: list = args if args is not None else []
        self.kwargs: dict = kwargs if kwargs is not None else {}
        self.finished = Event()
        self.running = Event()
        self.running.set()

    def stop(self) -> None:
        """ terminate timer's thread and stop the timer """
        self.resume()
        self.finished.set()

    def pause(self) -> None:
        self.running.clear()

    def resume(self) -> None:
        self.running.set()

    def run(self) -> None:
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
            self.running.wait()


class Timer:
    def __init__(self, interval: float = -1) -> None:
        self._timer: RepeatedTimer | None = None
        self.started: bool = False
        self.paused: bool = False
        self._interval: float = interval
        self._arrived: bool = False

    def set_interval_sec(self, interval: float) -> None:
        if interval <= 0:
            raise ValueError(f"the interval of Timer must be > 0, current: {interval}")
        self._interval = interval
        if self.started:
            self._timer.interval = interval

    def _set_status(self) -> None:
        self._arrived = True
        # print("Timer arrived")

    def start(self) -> None:
        if self.paused:
            self._timer.resume()
            self.paused = False
            return
        if self._interval <= 0:
            raise ValueError(f"the interval of Timer must be > 0, current: {self._interval}")
        self.started = True
        self._timer = RepeatedTimer(self._interval, self._set_status)
        self._timer.start()

    def pause(self) -> None:
        if self.started:
            self._timer.pause()
            self.paused = True

    def stop(self) -> None:
        if self.started:
            self._timer.stop()
            self.started = False
        self._arrived = False

    @property
    def arrived(self) -> bool:
        if self._arrived:
            self._arrived = False
            return True
        return False


class Util:
    # timers made by pygame event
    user_event_count: int = 0
    user_timer_list: list[int] = []

    # timers using builtin threading.Timer
    timer_list: list[Timer] = []

    @classmethod
    def timer(cls, interval: float = 0) -> Timer:
        """ generate timer using builtin threading """
        _timer = Timer(interval)
        cls.timer_list.append(_timer)
        return _timer

    @classmethod
    def generate_user_event_id(cls, timer=False) -> int:
        """ generate pygame `USEREVENT` id """
        new_id = cls.user_event_count + pygame.USEREVENT
        cls.user_event_count += 1
        if timer:
            cls.user_timer_list.append(new_id)
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
            raise ValueError(f"arg 'value' must be greater than 1.0, passed in {value = }")
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

    @classmethod
    def quit_game(cls) -> NoReturn:
        for timer in cls.timer_list:
            timer.stop()
        print("\033[1;36mBye.\033[0m")
        pygame.quit()
        sys.exit()
