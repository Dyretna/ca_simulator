# src/pygame_automata/ui/pygame_ui/button.py

from abc import ABC, abstractmethod

import pygame


class ButtonBase(ABC):
    """
    Base class for all buttons.

    Buttons are dumb:
    - they know their rect and hover state
    - they can draw themselves
    - they can detect hover and clicks
    - they call a callback when clicked
    """

    def __init__(self, x: int, y: int, w: int, h: int, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.callback: callable = callback
        self.hover: bool = False

    @abstractmethod
    def draw(self, surface: pygame.Surface, offset_y: int):
        pass

    def on_mouse_move(self, local_pos: tuple[int, int]):
        """Update hover state based on mouse movement."""

        self.hover = self.rect.collidepoint(local_pos)

    def on_mouse_down(self, local_pos: tuple[int, int]):
        """Handle mouse down in local coordinates."""

        if self.rect.collidepoint(local_pos):
            self.callback()

    def on_mouse_up(self, local_pos: tuple[int, int]):
        """Mouse up hook for future use (e.g. press/release logic)."""
        # kept for future expansion (press/release distinction)
        pass


class TextButton(ButtonBase):
    """Button that renders a text label."""

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str,
        font: pygame.font.Font,
        bg_color: tuple[int, int, int],
        text_color: tuple[int, int, int],
        callback: callable,
    ):
        super().__init__(x, y, w, h, callback)
        self.label = label
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color

    def draw(self, surface: pygame.Surface, offset_y: int):
        color = (
            self.bg_color
            if not self.hover
            else (
                min(self.bg_color[0] + 20, 255),
                min(self.bg_color[1] + 20, 255),
                min(self.bg_color[2] + 20, 255),
            )
        )

        pygame.draw.rect(
            surface,
            color,
            (self.rect.x, self.rect.y + offset_y, self.rect.w, self.rect.h),
            border_radius=6,
        )

        text = self.font.render(self.label, True, self.text_color)
        tx = self.rect.x + (self.rect.w - text.get_width()) // 2
        ty = self.rect.y + offset_y + (self.rect.h - text.get_height()) // 2
        surface.blit(text, (tx, ty))


class IconButtonBase(ButtonBase, ABC):
    """Base class for icon buttons."""

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        bg_color: tuple[int, int, int],
        hover_color: tuple[int, int, int],
        icon_color: tuple[int, int, int],
        callback: callable,
    ):
        super().__init__(x, y, w, h, callback)
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.icon_color = icon_color

    def draw(self, surface: pygame.Surface, offset_y: int):
        color = self.hover_color if self.hover else self.bg_color

        pygame.draw.rect(
            surface,
            color,
            (self.rect.x, self.rect.y + offset_y, self.rect.w, self.rect.h),
            border_radius=6,
        )

        cx = self.rect.x + self.rect.w // 2
        cy = self.rect.y + offset_y + self.rect.h // 2

        self.draw_icon(surface, cx, cy)

    @abstractmethod
    def draw_icon(self, surface: pygame.Surface, cx: int, cy: int):
        """Draw the icon at the given center position."""
        pass


class PlayButton(IconButtonBase):
    """Play icon: right-pointing triangle."""

    def draw_icon(self, surface: pygame.Surface, cx: int, cy: int):
        size = self.rect.h // 3
        points = [
            (cx - size // 2, cy - size),
            (cx - size // 2, cy + size),
            (cx + size, cy),
        ]
        pygame.draw.polygon(surface, self.icon_color, points)


class PauseButton(IconButtonBase):
    """Pause icon: two vertical bars."""

    def draw_icon(self, surface: pygame.Surface, cx: int, cy: int):
        bar_w = self.rect.w // 8
        bar_h = self.rect.h // 2
        gap = bar_w * 2

        pygame.draw.rect(
            surface,
            self.icon_color,
            (cx - gap, cy - bar_h // 2, bar_w, bar_h),
        )
        pygame.draw.rect(
            surface,
            self.icon_color,
            (cx + gap - bar_w, cy - bar_h // 2, bar_w, bar_h),
        )


# ----------------------------------------------
# CURRENTLY NOT IN USE
# maybe in later extension
# ----------------------------------------------


class NextButton(IconButtonBase):
    """Next icon: double right-pointing triangles."""

    def draw_icon(self, surface: pygame.Surface, cx: int, cy: int):
        size = self.rect.h // 3
        t1 = [(cx - size, cy - size), (cx - size, cy + size), (cx, cy)]
        t2 = [(cx, cy - size), (cx, cy + size), (cx + size, cy)]
        pygame.draw.polygon(surface, self.icon_color, t1)
        pygame.draw.polygon(surface, self.icon_color, t2)


class SaveButton(IconButtonBase):
    """Save icon: square "disk" with inner square."""

    def draw_icon(self, surface: pygame.Surface, cx: int, cy: int):
        size = self.rect.h // 3
        outer_rect = pygame.Rect(cx - size, cy - size, size * 2, size * 2)
        inner_rect = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
        pygame.draw.rect(surface, self.icon_color, outer_rect)
        pygame.draw.rect(surface, (0, 0, 0), inner_rect)
