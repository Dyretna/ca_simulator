# src/pygame_automata/ui/pygame_ui/bottom_bar.py

import pygame

from .button import ButtonBase


class UIBar:
    """
    Bottom UI bar that holds buttons and rule info.

    It is dumb: it only knows how to draw itself and forward mouse events
    to its buttons in local coordinates.
    """

    def __init__(
        self,
        height: int,
        bg_color: tuple[int, int, int],
        text_color: tuple[int, int, int],
        font: pygame.font.Font,
    ):
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font

        self.buttons: list[ButtonBase] = []
        self.offset_y: int = 0

    def add_button(self, btn: ButtonBase):
        self.buttons.append(btn)

    def draw(self, surface: pygame.Surface, rule_code: int):
        w = surface.get_width()
        h = surface.get_height()

        self.offset_y = h - self.height

        pygame.draw.rect(
            surface,
            self.bg_color,
            (0, self.offset_y, w, self.height),
        )

        text = self.font.render(f"Rule: {rule_code}", True, self.text_color)
        surface.blit(text, (10, self.offset_y + 15))

        for btn in self.buttons:
            btn.draw(surface, self.offset_y)

    def _to_local(self, screen_pos: tuple[int, int]) -> tuple[int, int]:
        """Convert screen coordinates to local UI bar coordinates."""

        return screen_pos[0], screen_pos[1] - self.offset_y

    def on_mouse_move(self, screen_pos: tuple[int, int]):
        """Handle mouse movement in screen coordinates."""

        local_pos = self._to_local(screen_pos)
        for btn in self.buttons:
            btn.on_mouse_move(local_pos)

    def on_mouse_down(self, screen_pos: tuple[int, int]):
        """Handle mouse down in screen coordinates."""

        local_pos = self._to_local(screen_pos)
        for btn in self.buttons:
            btn.on_mouse_down(local_pos)

    def on_mouse_up(self, screen_pos: tuple[int, int]):
        """Handle mouse up in screen coordinates."""

        local_pos = self._to_local(screen_pos)
        for btn in self.buttons:
            btn.on_mouse_up(local_pos)
