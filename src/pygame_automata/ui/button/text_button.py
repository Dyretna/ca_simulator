import pygame

from pygame_automata.ui.theme import (
    SETTINGS_BUTTON_BG,
    SETTINGS_BUTTON_FG,
    SETTINGS_BUTTON_HOVER,
)

from .base import ButtonBase


class TextButton(ButtonBase):
    def __init__(self, x, y, w, h, text, font, callback):
        super().__init__(x, y, w, h, callback)
        self.text = text
        self.font = font
        self.bg = SETTINGS_BUTTON_BG
        self.fg = SETTINGS_BUTTON_FG
        self.hover_color = SETTINGS_BUTTON_HOVER

        self.text_surf = self.font.render(self.text, True, self.fg)
        self.text_x = x + (w - self.text_surf.get_width()) // 2
        self.text_y = y + (h - self.text_surf.get_height()) // 2

    def draw(self, surface, offset_y):
        rect = pygame.Rect(
            self.rect.x, self.rect.y + offset_y, self.rect.w, self.rect.h
        )
        color = self.hover_color if self.hover else self.bg
        pygame.draw.rect(surface, color, rect, border_radius=6)
        surface.blit(self.text_surf, (self.text_x, self.text_y + offset_y))

    def on_mouse_move(self, local_pos):
        self.hover = self.rect.collidepoint(local_pos)

    def on_mouse_down(self, local_pos):
        if self.rect.collidepoint(local_pos):
            self.callback()
