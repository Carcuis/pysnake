import pygame
from pygame.locals import *
from settings import Global, KeyBoard
from event_manager import EventManager


class Text:
    def __init__(self, parent_surface: pygame.Surface):
        self._parent_surface = parent_surface
        self.text_array = []

    def add(self, text:str, color, position, alpha=255, bg_color=None, name:str="",
            font_size=Global.UI_SCALE, bold=False, italic=False, button=None):
        self.text_array.append({
            "name": name,
            "text": text,
            "color": color,
            "bg_color": bg_color,
            "alpha": alpha,
            "position": position,
            "font_name": "resources/fonts/font_bold.otf" if bold else "resources/fonts/font.otf",
            "font_size": font_size,
            "bold": bold,
            "italic": italic,
            "button": button
        })

    def render(self):
        coordinate: tuple[int, int]|tuple[int, int, int]
        parent_surface_width = self._parent_surface.get_width()
        parent_surface_height = self._parent_surface.get_height()

        for text in self.text_array:
            text_surface = pygame.font.Font(text["font_name"], text["font_size"]) \
                .render(text["text"], True, text["color"], text["bg_color"])
            text_surface_width = text_surface.get_width()
            text_surface_height = text_surface.get_height()

            if isinstance(text["position"], str):
                position = text["position"]
                if position == "left_top":
                    coordinate = (0, 0)
                elif position == "middle_top":
                    coordinate = (int((parent_surface_width - text_surface_width) / 2), 0)
                elif position == "right_top":
                    coordinate = (parent_surface_width - text_surface_width, 0)
                elif position == "left_bottom":
                    coordinate = (0, parent_surface_height - text_surface_height)
                elif position == "middle_bottom":
                    coordinate = (int((parent_surface_width - text_surface_width) / 2),
                                parent_surface_height - text_surface_height)
                elif position == "right_bottom":
                    coordinate = (parent_surface_width - text_surface_width,
                                parent_surface_height - text_surface_height)
                elif position == "left_middle":
                    coordinate = (0, int((parent_surface_height - text_surface_height) / 2))
                elif position == "right_middle":
                    coordinate = (parent_surface_width - text_surface_width,
                                int((parent_surface_height - text_surface_height) / 2))
                elif position == "center":
                    coordinate = (int((parent_surface_width - text_surface_width) / 2),
                                int((parent_surface_height - text_surface_height) / 2))
            elif isinstance(text["position"], tuple):
                '''
                custom position
                position = (
                    ratio_x,
                    ratio_y,
                    base_vertex={"auto"(default), "center", "left_top", "left_bottom", "right_top", "right_bottom"}
                )
                '''
                ratio_x = text["position"][0]
                ratio_y = text["position"][1]
                if len(text["position"]) == 2:
                    coordinate = ((parent_surface_width - text_surface_width) * ratio_x,
                                (parent_surface_height - text_surface_height) * ratio_y)
                elif len(text["position"]) == 3:
                    base_vertex = text["position"][2]
                    if base_vertex == "left_top":
                        coordinate = (int(parent_surface_width * ratio_x),
                                    int(parent_surface_height * ratio_y))
                    elif base_vertex == "left_bottom":
                        coordinate = (int(parent_surface_width * ratio_x),
                                    int(parent_surface_height * ratio_y - text_surface_height))
                    elif base_vertex == "right_up":
                        coordinate = (int(parent_surface_width * ratio_x - text_surface_width),
                                    int(parent_surface_height * ratio_y))
                    elif base_vertex == "right_bottom":
                        coordinate = (int(parent_surface_width * ratio_x - text_surface_width),
                                    int(parent_surface_height * ratio_y - text_surface_height))
                    elif base_vertex == "center":
                        coordinate = (int(parent_surface_width * ratio_x - text_surface_width / 2),
                                    int(parent_surface_height * ratio_y - text_surface_height / 2))

            text_surface.set_alpha(text["alpha"])
            if text["button"]:
                text["button"].rect = text_surface.get_rect()
                text["button"].rect.topleft = (coordinate[0], coordinate[1])
            self._parent_surface.blit(text_surface, coordinate)

    def clear(self):
        self.text_array.clear()


class Board:
    def __init__(self, parent_surface: pygame.Surface):
        self.text = Text(parent_surface)

    def draw(self):
        self.text.render()
        self.text.clear()


class Button:
    def __init__(self, title: str, color: tuple, position: tuple, alpha: tuple = (200, 255),
                 bg_color=None, font_size=2 * Global.UI_SCALE):
        self.is_hovered_or_selected = False
        self.is_triggered = False
        self.rect = pygame.Rect(-1, -1, 1, 1)
        self.title = title
        self._content = dict()
        self._color = color
        self._alpha = alpha
        self._position = position
        self._bg_color = bg_color
        self._font_size = font_size

    def update_status(self, _event_manager: EventManager):
        """
        Update button's hover and click status.
        :param _event_manager: in game event_manager
        """
        if self.rect.collidepoint(_event_manager.mouse_pos):
            self.is_hovered_or_selected = True
            self.is_triggered = _event_manager.check_key_or_button(MOUSEBUTTONUP, 1)
        else:
            self.is_hovered_or_selected = False
            self.is_triggered = False

    def get_content(self):
        """
        Generate content of button for Text.add().
        :return: Dict
        """
        self._content["name"] = self.title
        self._content["position"] = self._position
        self._content["bg_color"] = self._bg_color
        self._content["font_size"] = self._font_size
        self._content["button"] = self

        if not self.is_hovered_or_selected:
            self._content["text"] = self.title
            self._content["color"] = self._color[0]
            self._content["alpha"] = self._alpha[0]
            self._content["bold"] = False
        else:
            self._content["text"] = f"> {self.title} <"
            self._content["color"] = self._color[1]
            self._content["alpha"] = self._alpha[1]
            self._content["bold"] = True
        return self._content


class ButtonManager:
    def __init__(self, *buttons: Button):
        self.button_list: list[Button] = list(buttons)
        self.button_count = len(buttons)
        self._mouse_mode = True
        self._keyboard_mode = False
        self.selected_index = 0
        self._previous_selected_index = self.selected_index

    def update_status(self, _event_manager: EventManager):
        """
        Update all buttons' hover and click status through mouse and keyboard control.
        :param _event_manager: in-game event_manager
        """

        ''' switch between mouse mode and keyboard mode '''
        if _event_manager.match_event_type(MOUSEMOTION):
            self._mouse_mode = True
            self._keyboard_mode = False
        if _event_manager.check_key_or_button(KEYDOWN, KeyBoard.up_list) or \
                _event_manager.check_key_or_button(KEYDOWN, KeyBoard.down_list):
            self._mouse_mode = False
            self._keyboard_mode = True

        ''' update by mouse '''
        if self._mouse_mode:
            for button in self.button_list:
                button.update_status(_event_manager)

        ''' update current selected index '''
        for i in range(self.button_count):
            if self.button_list[i].is_hovered_or_selected:
                self.selected_index = i
                break

        ''' update by keyboard '''
        if _event_manager.check_key_or_button(KEYDOWN, KeyBoard.up_list):
            self._go_previous()
        if _event_manager.check_key_or_button(KEYDOWN, KeyBoard.down_list):
            self._go_next()

        ''' finally update selected status of buttons '''
        self.button_list[self._previous_selected_index].is_hovered_or_selected = False
        self.button_list[self.selected_index].is_hovered_or_selected = True
        if self.button_list[self.selected_index].is_hovered_or_selected:
            if _event_manager.check_key_or_button(KEYDOWN, KeyBoard.select_list):
                self.button_list[self.selected_index].is_triggered = True

    def _go_next(self):
        self._previous_selected_index = self.selected_index
        self.selected_index += 1
        if self.selected_index >= self.button_count:
            self.selected_index = 0

    def _go_previous(self):
        self._previous_selected_index = self.selected_index
        self.selected_index -= 1
        if self.selected_index < 0:
            self.selected_index = self.button_count - 1

    def add_text_to_board(self, _text_board: Board):
        for button in self.button_list:
            _text_board.text.add(**button.get_content())
