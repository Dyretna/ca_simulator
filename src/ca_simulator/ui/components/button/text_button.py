from typing import Callable, Optional

import pygame

from pygame_automata.ui.theme import (
    BTN_TEXT_C,
    DEFAULT_FONT,
    SETTINGS_BUTTON_ACTIVE,
    SETTINGS_BUTTON_BG,
    SETTINGS_BUTTON_HOVER,
    SETTINGS_ROW_LABEL_C,
)

from .base import ButtonBase


class TextButton(ButtonBase):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        text: str,
        font: pygame.font.Font,
        callback: Callable,
        active: Optional[bool] = None,
    ):
        super().__init__(x, y, w, h, callback)
        self.text = text
        self.font = font

        self.bg = SETTINGS_BUTTON_BG
        self.hover_color = SETTINGS_BUTTON_HOVER
        self.active_color = SETTINGS_BUTTON_ACTIVE
        self.text_color = BTN_TEXT_C

        self.active = active

        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_x = x + (w - self.text_surf.get_width()) // 2
        self.text_y = y + (h - self.text_surf.get_height()) // 2

    def draw(self, surface):
        rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h)

        if self.active:
            color = self.active_color
        elif self.hover:
            color = self.hover_color
        else:
            color = self.bg

        pygame.draw.rect(surface, color, rect, border_radius=6)
        surface.blit(self.text_surf, (self.text_x, self.text_y))

    def on_mouse_move(self, local_pos):
        self.hover = self.rect.collidepoint(local_pos)

    def on_mouse_down(self, local_pos):
        if self.rect.collidepoint(local_pos):
            self.callback()


# ------------------------------------------------------------
# TextButtonRow: simple row with label + TextButtons
# ------------------------------------------------------------
class TextButtonRow:
    def __init__(self, x: int, y: int, label: str):
        self.x = x
        self.y = y
        self.label = label
        self.buttons: list[TextButton] = []
        self.font = pygame.font.SysFont(**DEFAULT_FONT)
        self.label_offset = 200

    def add(self, text: str, callback: Callable, active: bool):
        # width based on pixel width of text
        width = self.font.size(text)[0] + 10
        height = self.font.size(text)[1] + 5
        btn = TextButton(0, 0, width, height, text, self.font, callback, active)
        self.buttons.append(btn)

    def draw(self, panel: pygame.Surface):
        # label
        label_surf = self.font.render(self.label, True, SETTINGS_ROW_LABEL_C)
        panel.blit(label_surf, (20, self.y))

        # draw buttons horizontally
        x = self.x + self.label_offset
        for btn in self.buttons:
            # set pos in panel
            btn.rect.x = x
            btn.rect.y = self.y

            # center text in button
            btn.text_x = btn.rect.x + (btn.rect.w - btn.text_surf.get_width()) // 2
            btn.text_y = btn.rect.y + (btn.rect.h - btn.text_surf.get_height()) // 2

            # draw on panel
            btn.draw(panel)

            # next butt assumes position
            x += btn.rect.w + 10

    def handle_mouse_move(self, pos):
        for btn in self.buttons:
            btn.on_mouse_move(pos)

    def handle_mouse_down(self, pos):
        for btn in self.buttons:
            if btn.rect.collidepoint(pos):
                btn.active = True

                for other in self.buttons:
                    if other is not btn:
                        other.active = False

            btn.on_mouse_down(pos)
