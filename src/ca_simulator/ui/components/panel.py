from typing import Callable

import pygame

from ..theme import SETTINGS_PANEL_BG
from .settings_components import TextButton


class UIPanel:
    """
    A simple base panel used by modal views.

    UIPanel provides a centered surface with consistent styling, padding
    and geometry. Views can choose their own size via width_ratio and
    height_ratio, but share the same visual layout. The panel also offers
    a helper for placing Apply and Cancel buttons in a uniform bottom
    position.
    """

    def __init__(
        self, width_ratio: float = 0.6, height_ratio: float = 0.6, padding: int = 60
    ):
        w, h = pygame.display.get_window_size()
        self.w = int(w * width_ratio)
        self.h = int(h * height_ratio)
        self.x = (w - self.w) // 2
        self.y = (h - self.h) // 2
        self.padding = padding

        self.surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.surface.fill(SETTINGS_PANEL_BG)

    def place_bottom_buttons(
        self, font: pygame.font.Font, apply_cb: Callable, cancel_cb: Callable
    ) -> None:
        btn_w = 100
        btn_h = 40
        spacing = 20

        btn_y = self.y + self.h - self.padding - btn_h

        cancel_x = self.x + self.w - self.padding - btn_w
        apply_x = cancel_x - spacing - btn_w

        self.apply_button = TextButton(
            apply_x, btn_y, btn_w, btn_h, "Apply", font, apply_cb
        )
        self.cancel_button = TextButton(
            cancel_x, btn_y, btn_w, btn_h, "Cancel", font, cancel_cb
        )
