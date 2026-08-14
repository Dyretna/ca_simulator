from pathlib import Path
from typing import Callable

import pygame

from .base import ButtonBase


class ColorSwatchButton(ButtonBase):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        get_color: Callable[[], pygame.Color],
        icon_path: Path,
        callback: Callable[[], None],
    ):
        super().__init__(x, y, w, h, callback)

        self.get_color: Callable[[], pygame.Color] = get_color
        self.radius: int = min(w, h) // 2
        img = pygame.image.load(icon_path).convert_alpha()
        diameter: int = self.radius * 2
        self.icon_img: pygame.Surface = pygame.transform.smoothscale(
            img, (diameter, diameter)
        )

    def on_mouse_move(self, local_pos: tuple[int, int]) -> None:
        pass

    def on_mouse_down(self, local_pos: tuple[int, int]) -> None:
        dx: int = local_pos[0] - self.rect.centerx
        dy: int = local_pos[1] - self.rect.centery
        if dx * dx + dy * dy <= self.radius * self.radius:
            self.callback()

    def draw(self, surface: pygame.Surface, offset_y: int) -> None:
        cx: int = self.rect.centerx
        cy: int = self.rect.centery + offset_y
        color: pygame.Color = self.get_color()
        pygame.draw.circle(surface, color, (cx, cy), self.radius)
        img: pygame.Surface = self.icon_img
        x: int = cx - img.get_width() // 2
        y: int = cy - img.get_height() // 2
        surface.blit(img, (x, y))
