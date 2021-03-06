import pygame
from pygame.locals import *
from settings import Global, KeyBoard
from event_manager import EventManager


class Text:
    def __init__(self, parent_surface: pygame.Surface):
        self._parent_surface = parent_surface
        self.text_array = []

    def add(self, text: str, color, position, alpha=255, bg_color=None, name: str = None,
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
        position: tuple = ()
        for text in self.text_array:
            text_surface = pygame.font.Font(text["font_name"], text["font_size"]) \
                .render(text["text"], True, text["color"], text["bg_color"])

            if isinstance(text["position"], str):
                ''' specific positions '''
                if text["position"] == "left_top":
                    position = (0, 0)
                elif text["position"] == "middle_top":
                    position = ((self._parent_surface.get_width() - text_surface.get_width()) / 2, 0)
                elif text["position"] == "right_top":
                    position = (self._parent_surface.get_width() - text_surface.get_width(), 0)
                elif text["position"] == "left_bottom":
                    position = (0, self._parent_surface.get_height() - text_surface.get_height())
                elif text["position"] == "middle_bottom":
                    position = ((self._parent_surface.get_width() - text_surface.get_width()) / 2,
                                self._parent_surface.get_height() - text_surface.get_height())
                elif text["position"] == "right_bottom":
                    position = (self._parent_surface.get_width() - text_surface.get_width(),
                                self._parent_surface.get_height() - text_surface.get_height())
                elif text["position"] == "left_middle":
                    position = (0, (self._parent_surface.get_height() - text_surface.get_height()) / 2)
                elif text["position"] == "right_middle":
                    position = (self._parent_surface.get_width() - text_surface.get_width(),
                                (self._parent_surface.get_height() - text_surface.get_height()) / 2)
                elif text["position"] == "center":
                    position = ((self._parent_surface.get_width() - text_surface.get_width()) / 2,
                                (self._parent_surface.get_height() - text_surface.get_height()) / 2)
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
                    position = ((self._parent_surface.get_width() - text_surface.get_width()) * ratio_x,
                                (self._parent_surface.get_height() - text_surface.get_height()) * ratio_y)
                elif len(text["position"]) == 3:
                    if text["position"] == "left_top":
                        position = ((self._parent_surface.get_width() * ratio_x),
                                    (self._parent_surface.get_height() * ratio_y))
                    elif text["position"] == "left_bottom":
                        position = ((self._parent_surface.get_width() * ratio_x),
                                    (self._parent_surface.get_height() * ratio_y - text_surface.get_height()))
                    elif text["position"] == "right_up":
                        position = ((self._parent_surface.get_width() * ratio_x - text_surface.get_width()),
                                    (self._parent_surface.get_height() * ratio_y))
                    elif text["position"] == "right_bottom":
                        position = ((self._parent_surface.get_width() * ratio_x - text_surface.get_width()),
                                    (self._parent_surface.get_height() * ratio_y - text_surface.get_height()))
                    elif text["position"] == "center":
                        position = ((self._parent_surface.get_width() * ratio_x - text_surface.get_width() / 2),
                                    (self._parent_surface.get_height() * ratio_y - text_surface.get_height() / 2))

            text_surface.set_alpha(text["alpha"])
            if text["button"]:
                text["button"].rect = text_surface.get_rect()
                text["button"].rect.topleft = (position[0], position[1])
            self._parent_surface.blit(text_surface, position)

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
        self._param_dict = dict()
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

    def get_param_list(self):
        """
        Generate button's to-text param.
        :return: Dict
        """
        self._param_dict["name"] = self.title
        self._param_dict["position"] = self._position
        self._param_dict["bg_color"] = self._bg_color
        self._param_dict["font_size"] = self._font_size
        self._param_dict["button"] = self

        if not self.is_hovered_or_selected:
            self._param_dict["text"] = self.title
            self._param_dict["color"] = self._color[0]
            self._param_dict["alpha"] = self._alpha[0]
            self._param_dict["bold"] = False
        else:
            self._param_dict["text"] = f"> {self.title} <"
            self._param_dict["color"] = self._color[1]
            self._param_dict["alpha"] = self._alpha[1]
            self._param_dict["bold"] = True
        return self._param_dict


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
            _text_board.text.add(**button.get_param_list())
