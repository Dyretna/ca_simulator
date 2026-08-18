"""
Components used by the Settings view.

TextButtonRow and SettingsColumn provide simple UI structures for
labelled button rows and vertical settings layouts. They are kept
inside settings_components to show which view uses them. If needed,
they can be made more abstract later, but for now the design is kept
minimal and straightforward.
"""

from typing import Callable

import pygame

from ..theme import DEFAULT_FONT, TEXT_ACTIVE
from .button import TextButton


class TextButtonRow:
    """
    A horizontal row of text buttons with a label.

    This implementation expects self.x/self.y to be set to GLOBAL coordinates
    by the caller (SettingsColumn) before draw() is anropad. draw() updates
    each button.rect to global coords so event handling can use event.pos directly.
    """

    def __init__(self, label: str):
        # Do not assume global position at construction time.
        # SettingsColumn will set row.x and row.y before draw().
        self.x: int = 0
        self.y: int = 0
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

    def draw(self, surface: pygame.Surface):
        # label (self.x/self.y must be global)
        label_surf = self.font.render(self.label, True, TEXT_ACTIVE)
        surface.blit(label_surf, (self.x, self.y))

        # draw buttons using global coords
        x = self.x + self.label_offset
        for btn in self.buttons:
            # set btn rect to global position
            # before any collision checks
            btn.rect.topleft = (x, self.y)

            # center text in button
            btn.text_x = btn.rect.x + (btn.rect.w - btn.text_surf.get_width()) // 2
            btn.text_y = btn.rect.y + (btn.rect.h - btn.text_surf.get_height()) // 2

            # draw button
            btn.draw(surface)
            x += btn.rect.w + 10

    def handle_mouse_move(self, pos):
        # pos is global
        # TextButton.on_mouse_move expects global pos
        for btn in self.buttons:
            btn.on_mouse_move(pos)

    def handle_mouse_down(self, pos):
        # pos is global
        # check collidepoint against global rects
        for btn in self.buttons:
            if btn.rect.collidepoint(pos):
                # clicked: set active state
                btn.active = True
                for other in self.buttons:
                    if other is not btn:
                        other.active = False

            # still call on_mouse_down so button can run
            # callback if implemented there
            btn.on_mouse_down(pos)


class SettingsColumn:
    """
    A vertical collection of TextButtonRow instances.

    Each added row represents a labelled setting with selectable values.
    SettingsColumn handles layout, drawing and input dispatching for all
    rows. Views using this component are responsible for calling draw()
    and forwarding mouse events.
    """

    def __init__(self, padding: int, row_height: int):
        self.padding = padding
        self.row_height = row_height
        self.rows: list[TextButtonRow] = []

    def add_row(self, label: str, values, setter, is_active):
        row = TextButtonRow(label)

        for v in values:
            active = is_active(v)
            text = "ON" if v is True else "OFF" if v is False else str(v)
            row.add(text, lambda v=v: setter(v), active)

        self.rows.append(row)

    def draw(self, surface, offset_y=0, start_x=None):
        """
        Draw rows using global coordinates.

        start_x must be provided (global X).
        offset_y is global Y where the column starts.
        """
        assert start_x is not None, "SettingsColumn.draw requires start_x (global X)"

        y = offset_y
        for row in self.rows:
            # set global position for the row before drawing
            row.x = start_x
            row.y = y
            row.draw(surface)
            y += self.row_height

    def handle_mouse_move(self, pos):
        for row in self.rows:
            row.handle_mouse_move(pos)

    def handle_mouse_down(self, pos):
        for row in self.rows:
            row.handle_mouse_down(pos)
