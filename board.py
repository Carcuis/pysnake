import pygame
from settings import *


class Text:
    def __init__(self, parent_surface):
        self.text_array = []
        self.parent_surface = parent_surface
        self.text_surface_array = []

    def add(self,
            text,
            color,
            position,
            alpha=255,
            bg_color=None,
            name=None,
            font_size=Global.UI_SCALE,
            bold=False,
            italic=False):
        self.text_array.append(
            {
                "text": text,
                "color": color,
                "alpha": alpha,
                "position": position,
                "bg_color": bg_color,
                "name": name,
                "font_name": "resources/fonts/font_bold.otf" if bold else "resources/fonts/font.otf",
                "font_size": font_size,
                "bold": bold,
                "italic": italic
            }
        )

    def render(self):
        position = ()
        for text in self.text_array:
            text_surface = pygame.font.Font(text["font_name"], text["font_size"])\
                .render(text["text"], True, text["color"], text["bg_color"])

            if isinstance(text["position"], str):
                ''' specific positions '''
                if text["position"] == "left_top":
                    position = (0, 0)
                elif text["position"] == "middle_top":
                    position = ((self.parent_surface.get_width() - text_surface.get_width())/2, 0)
                elif text["position"] == "right_top":
                    position = (self.parent_surface.get_width() - text_surface.get_width(), 0)
                elif text["position"] == "left_bottom":
                    position = (0, self.parent_surface.get_height() - text_surface.get_height())
                elif text["position"] == "middle_bottom":
                    position = ((self.parent_surface.get_width() - text_surface.get_width())/2,
                                self.parent_surface.get_height() - text_surface.get_height())
                elif text["position"] == "right_bottom":
                    position = (self.parent_surface.get_width() - text_surface.get_width(),
                                self.parent_surface.get_height() - text_surface.get_height())
                elif text["position"] == "left_middle":
                    position = (0, (self.parent_surface.get_height() - text_surface.get_height())/2)
                elif text["position"] == "right_middle":
                    position = (self.parent_surface.get_width() - text_surface.get_width(),
                                (self.parent_surface.get_height() - text_surface.get_height())/2)
                elif text["position"] == "center":
                    position = ((self.parent_surface.get_width() - text_surface.get_width())/2,
                                (self.parent_surface.get_height() - text_surface.get_height())/2)
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
                    position = ((self.parent_surface.get_width() - text_surface.get_width()) * ratio_x,
                                (self.parent_surface.get_height() - text_surface.get_height()) * ratio_y)
                elif len(text["position"]) == 3:
                    if text["position"] == "left_top":
                        position = ((self.parent_surface.get_width() * ratio_x),
                                    (self.parent_surface.get_height() * ratio_y))
                    elif text["position"] == "left_bottom":
                        position = ((self.parent_surface.get_width() * ratio_x),
                                    (self.parent_surface.get_height() * ratio_y - text_surface.get_height()))
                    elif text["position"] == "right_up":
                        position = ((self.parent_surface.get_width() * ratio_x - text_surface.get_width()),
                                    (self.parent_surface.get_height() * ratio_y))
                    elif text["position"] == "right_bottom":
                        position = ((self.parent_surface.get_width() * ratio_x - text_surface.get_width()),
                                    (self.parent_surface.get_height() * ratio_y - text_surface.get_height()))
                    elif text["position"] == "center":
                        position = ((self.parent_surface.get_width() * ratio_x - text_surface.get_width() / 2),
                                    (self.parent_surface.get_height() * ratio_y - text_surface.get_height() / 2))

            text_surface.set_alpha(text["alpha"])
            text["left_top"] = position
            self.text_surface_array.append(text_surface)
            self.parent_surface.blit(text_surface, position)

    def clear(self):
        self.text_array = []
        self.text_surface_array = []


class Board:
    def __init__(self, parent_surface):
        self.text = Text(parent_surface)

    def draw(self):
        self.text.render()

    def clear(self):
        self.text.clear()

#
# class ForbiddenZone:
#     def __init__(self):
#         self.top_padding = TOP_PADDING
#         self.bottom_padding = BOTTOM_PADDING
#         self.left_padding = LEFT_PADDING
#         self.right_padding = RIGHT_PADDING
