from typing import Callable

import pygame

from ..theme import DEFAULT_FONT, TEXT_ACTIVE
from .button import TextButton


class TextButtonRow:
    def __init__(self, x: int, label: str):
        self.x = x
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

    def draw(self, panel: pygame.Surface, y: int):
        # label
        label_surf = self.font.render(self.label, True, TEXT_ACTIVE)
        panel.blit(label_surf, (self.x, y))

        # draw buttons horizontally
        x = self.x + self.label_offset
        for btn in self.buttons:
            # set pos in panel
            btn.rect.x = x
            btn.rect.y = y

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


class SettingsColumn:
    def __init__(self, padding: int, row_height: int):
        self.padding = padding
        self.row_height = row_height
        self.rows: list[TextButtonRow] = []

    def add_row(self, label: str, values, setter, is_active):
        row = TextButtonRow(self.padding, label)

        for v in values:
            active = is_active(v)
            text = "ON" if v is True else "OFF" if v is False else str(v)
            row.add(text, lambda v=v: setter(v), active)

        self.rows.append(row)

    def draw(self, surface, offset_y=0):
        y = offset_y
        for row in self.rows:
            row.draw(surface, y)
            y += self.row_height

    def handle_mouse_move(self, pos):
        for row in self.rows:
            row.handle_mouse_move(pos)

    def handle_mouse_down(self, pos):
        for row in self.rows:
            row.handle_mouse_down(pos)
