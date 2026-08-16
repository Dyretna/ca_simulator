from typing import Callable, Optional

import pygame

from ....ui.theme import (
    BTN_ACTIVE_C,
    BTN_HOVER_C,
    BTN_INACTIVE_C,
    TEXT_ACTIVE,
    TEXT_INACTIVE,
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

        self.hover_c = BTN_HOVER_C
        self.active_btn_c = BTN_ACTIVE_C
        self.inactive_btn_c = BTN_INACTIVE_C

        self.active_text_c = TEXT_ACTIVE
        self.inactive_text_c = TEXT_INACTIVE

        self.active = active

        # initial text cover
        self.text_color = self.active_text_c if self.active else self.inactive_text_c
        self.text_surf = self.font.render(self.text, True, self.text_color)

        self.text_x = x + (w - self.text_surf.get_width()) // 2
        self.text_y = y + (h - self.text_surf.get_height()) // 2

    def draw(self, surface: pygame.Surface):
        if self.active:
            btn_color = self.active_btn_c
            text_color = self.active_text_c

        elif self.hover:
            btn_color = self.hover_c
            text_color = self.active_text_c
        else:
            btn_color = self.inactive_btn_c
            text_color = self.inactive_text_c

        self.text_surf = self.font.render(self.text, True, text_color)

        rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h)
        pygame.draw.rect(surface, btn_color, rect, border_radius=6)
        surface.blit(self.text_surf, (self.text_x, self.text_y))

    def on_mouse_move(self, local_pos):
        self.hover = self.rect.collidepoint(local_pos)

    def on_mouse_down(self, local_pos):
        if self.rect.collidepoint(local_pos):
            self.callback()
