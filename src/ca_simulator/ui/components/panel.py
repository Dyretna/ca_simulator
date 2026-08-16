import pygame

from ..theme import SETTINGS_PANEL_BG
from .settings_components import TextButton


class UIPanel:
    def __init__(self, width_ratio=0.6, height_ratio=0.6, padding=60):
        w, h = pygame.display.get_window_size()
        self.w = int(w * width_ratio)
        self.h = int(h * height_ratio)
        self.x = (w - self.w) // 2
        self.y = (h - self.h) // 2
        self.padding = padding

        self.surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.surface.fill(SETTINGS_PANEL_BG)

    def place_bottom_buttons(self, font, apply_cb, cancel_cb):
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
