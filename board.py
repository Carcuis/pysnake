import pygame

from event import EventManager
from settings import Global, KeyBoard


class Text:
    def __init__(self, text: str, color: pygame.Color, position: str | tuple[float, float] | tuple[float, float, str],
                 alpha=255, bg_color: tuple[pygame.Color, pygame.Color] | None = None, name: str = "",
                 font_size=Global.UI_SCALE, bold=False, italic=False, button: 'Button' = None) -> None:
        self.text: str = text
        self.color: pygame.Color = color
        self.bg_color: pygame.Color | None = bg_color
        self.position: str | tuple[float, float] | tuple[float, float, str] = position
        self.alpha: int = alpha
        self.name: str = name
        self.font_name: str = "resources/fonts/font_bold.otf" if bold else "resources/fonts/font.otf"
        self.font_size: int = font_size
        self.bold: bool = bold
        self.italic: bool = italic
        self.button: 'Button' = button


class TextManager:
    def __init__(self) -> None:
        self.text_array: list[Text] = []

    def add(self, text: Text) -> None:
        self.text_array.append(text)

    def draw(self, surface: pygame.Surface) -> None:
        coordinate: tuple[int, int] = (0, 0)
        parent_surface_width = surface.get_width()
        parent_surface_height = surface.get_height()

        for text in self.text_array:
            text_surface = pygame.font.Font(text.font_name, text.font_size) \
                .render(text.text, True, text.color, text.bg_color)
            text_surface_width = text_surface.get_width()
            text_surface_height = text_surface.get_height()

            if isinstance(text.position, str):
                position = text.position
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
            elif isinstance(text.position, tuple):
                '''
                custom position
                position = (
                    ratio_x,
                    ratio_y,
                    base_vertex={"auto"(default), "center", "left_top", "left_bottom", "right_top", "right_bottom"}
                )
                '''
                ratio_x = text.position[0]
                ratio_y = text.position[1]
                if len(text.position) == 2:
                    coordinate = ((parent_surface_width - text_surface_width) * ratio_x,
                                  (parent_surface_height - text_surface_height) * ratio_y)
                elif len(text.position) == 3:
                    base_vertex = text.position[2]
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

            text_surface.set_alpha(text.alpha)
            if text.button:
                text.button.rect = text_surface.get_rect()
                text.button.rect.topleft = coordinate
            surface.blit(text_surface, coordinate)

    def clear(self) -> None:
        self.text_array.clear()


class Button:
    def __init__(self, title: str, color: tuple[pygame.Color, pygame.Color],
                 position: str | tuple[float, float] | tuple[float, float, str],
                 alpha: tuple[int, int] = (200, 255), bg_color: tuple[pygame.Color, pygame.Color] | None = None,
                 font_size=2 * Global.UI_SCALE) -> None:
        self.is_hovered_or_selected = False
        self.is_triggered = False
        self.rect = pygame.Rect(-1, -1, 1, 1)
        self.title = title
        self._content: dict = {}
        self._color = color
        self._alpha = alpha
        self._position = position
        self._bg_color = bg_color
        self._font_size = font_size

    def update_status(self) -> None:
        """
        Update button's hover and click status.
        """
        if self.rect.collidepoint(EventManager.mouse_pos):
            self.is_hovered_or_selected = True
            self.is_triggered = EventManager.check_key_or_button(pygame.MOUSEBUTTONUP, 1)
        else:
            self.is_hovered_or_selected = False
            self.is_triggered = False

    def get_text(self) -> Text:
        """
        Generate content of button for Text.add().
        :return: Text
        """
        name = self.title
        position = self._position
        bg_color = self._bg_color
        font_size = self._font_size

        if not self.is_hovered_or_selected:
            text = self.title
            color = self._color[0]
            alpha = self._alpha[0]
            bold = False
        else:
            text = f"> {self.title} <"
            color = self._color[1]
            alpha = self._alpha[1]
            bold = True
        return Text(text, color, position, alpha, bg_color, name, font_size, bold, False, self)


class ButtonManager:
    def __init__(self) -> None:
        self.button_list: list[Button] = []
        self.button_count: int = 0
        self._mouse_mode = True
        self._keyboard_mode = False
        self._selected_index: int = 0
        self._previous_selected_index: int = 0

    def add(self, button: Button) -> None:
        self.button_list.append(button)
        self.button_count += 1

    def update_status(self) -> None:
        """
        Update all buttons' hover and click status through mouse and keyboard control.
        """

        ''' switch between mouse mode and keyboard mode '''
        if EventManager.match_event_type(pygame.MOUSEMOTION):
            self._mouse_mode = True
            self._keyboard_mode = False
        if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.up_list) or \
                EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.down_list):
            self._mouse_mode = False
            self._keyboard_mode = True

        ''' update by mouse '''
        if self._mouse_mode:
            for button in self.button_list:
                button.update_status()

        ''' update current selected index '''
        for i in range(self.button_count):
            if self.button_list[i].is_hovered_or_selected:
                self._selected_index = i
                break

        ''' update by keyboard '''
        if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.up_list):
            self._go_previous()
        if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.down_list):
            self._go_next()

        ''' finally update selected status of buttons '''
        self.button_list[self._previous_selected_index].is_hovered_or_selected = False
        self.button_list[self._selected_index].is_hovered_or_selected = True
        if self.button_list[self._selected_index].is_hovered_or_selected:
            if EventManager.check_key_or_button(pygame.KEYDOWN, KeyBoard.select_list):
                self.button_list[self._selected_index].is_triggered = True

    def _go_next(self) -> None:
        self._previous_selected_index = self._selected_index
        self._selected_index += 1
        if self._selected_index >= self.button_count:
            self._selected_index = 0

    def _go_previous(self) -> None:
        self._previous_selected_index = self._selected_index
        self._selected_index -= 1
        if self._selected_index < 0:
            self._selected_index = self.button_count - 1

    def clear(self) -> None:
        self.button_list.clear()
        self.button_count = 0
        self._previous_selected_index = 0
        self._selected_index = 0


class Board:
    def __init__(self) -> None:
        self._text_manager = TextManager()
        self._button_manager = ButtonManager()

    def add_text(self, *text: Text) -> None:
        for _text in text:
            self._text_manager.add(_text)

    def add_button(self, *button: Button) -> None:
        for _button in button:
            self._button_manager.add(_button)
            # self._text_manager.add(_button.get_text())

    def update_button_status(self) -> None:
        self._button_manager.update_status()

    def draw(self, surface: pygame.Surface) -> None:
        if self._button_manager.button_count > 0:
            for button in self._button_manager.button_list:
                self._text_manager.add(button.get_text())
        self._text_manager.draw(surface)
        self._text_manager.clear()

    def clear_button(self) -> None:
        self._button_manager.clear()
