from typing import Callable, Tuple

import pygame

from ..components import Slider, UIPanel
from ..theme import DEFAULT_FONT, SETTINGS_PANEL_BG, TITLE_FONT

ColorTuple = Tuple[int, int, int, int]


class ColorPicker:
    """
    Modal view for selecting a foreground or background color.

    ColorPicker displays a panel with RGB sliders, a live color preview,
    and Apply/Cancel controls. It manages its own active state, updates
    slider positions when shown, and returns the selected color through
    a callback supplied by the caller. The picker draws a dimmed overlay
    behind the panel and is responsible for closing itself via hide().

    Notes
    -----
    Colors are converted between (r, g, b, a) tuples and pygame.Color.
    The simulator stores colors as tuples to avoid accidental shared
    references: pygame.Color is mutable, and using it throughout the
    configuration layer risks old color objects lingering in memory or
    being mutated indirectly. Using tuples for config and pygame.Color
    only inside the UI keeps updates safe and predictable.
    """

    def __init__(self):
        self.active: bool = False

        self.return_callback = None
        self.color = pygame.Color(0, 0, 0, 255)

        # panel
        self.panel = UIPanel(width_ratio=0.5, height_ratio=0.35)

        # sliders
        self.rs = Slider(0, 255, 510)
        self.gs = Slider(0, 255, 510)
        self.bs = Slider(0, 255, 510)
        self.sliders = [self.rs, self.gs, self.bs]

        # the color display
        self.color_rect = pygame.Rect(0, 0, 0, 0)

        # fonts
        self.font = pygame.font.SysFont(**DEFAULT_FONT)
        self.title_font = pygame.font.SysFont(**TITLE_FONT)

    # --------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------

    def tuple_to_color(self, t: ColorTuple) -> pygame.Color:
        return pygame.Color(t[0], t[1], t[2], t[3])

    def color_to_tuple(self, c: pygame.Color) -> ColorTuple:
        return (c.r, c.g, c.b, c.a)

    def show(self, input_color: ColorTuple, callback: Callable):
        """Activate colorpicker screen."""
        self.active = True
        self.return_callback = callback

        self.panel.place_bottom_buttons(self.font, self._apply_changes, self.hide)

        c = self.tuple_to_color(input_color)
        self.c = c

        # set slider values
        self.rs.value = c.r
        self.gs.value = c.g
        self.bs.value = c.b

        # uppdate_handle Positions
        self.rs._update_handle()
        self.gs._update_handle()
        self.bs._update_handle()

        # update color
        self._update_color()
        self._build_sliders()
        self._build_color_rect()

    def hide(self):
        """Deactivate colorpicker screen."""
        self.active = False

    def is_active(self):
        return self.active

    def handle_event(self, event: pygame.event.Event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return

        if event.type not in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ):
            return

        for slider in self.sliders:
            slider.handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            self.panel.apply_button.on_mouse_move(event.pos)
            self.panel.cancel_button.on_mouse_move(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.panel.apply_button.on_mouse_down(event.pos)
            self.panel.cancel_button.on_mouse_down(event.pos)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        # dark overlay - dim background
        w, h = surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self.panel.surface.fill(SETTINGS_PANEL_BG)

        # color preview
        self._update_color()
        rgb = (self.color.r, self.color.g, self.color.b)
        pygame.draw.rect(self.panel.surface, rgb, self.color_rect, border_radius=10)
        pygame.draw.rect(
            self.panel.surface, (0, 0, 0), self.color_rect, width=3, border_radius=10
        )
        # blit
        surface.blit(self.panel.surface, (self.panel.x, self.panel.y))

        # sliders and buttons last
        for slider in self.sliders:
            slider.draw(surface)

        self.panel.apply_button.draw(surface)
        self.panel.cancel_button.draw(surface)

    # --------------------------------------------------------------
    # helpers
    # --------------------------------------------------------------

    def _build_sliders(self):
        y_inc = 70
        p = self.panel.padding
        self.rs.rect.topleft = (self.panel.x + p, self.panel.y + p)
        self.gs.rect.topleft = (self.panel.x + p, self.panel.y + p + y_inc)
        self.bs.rect.topleft = (self.panel.x + p, self.panel.y + p + y_inc * 2)

    def _build_color_rect(self):
        p = self.panel.padding
        width = 160
        panel_rect = self.panel.surface.get_rect()
        left = panel_rect.width - (width + p)
        top = p
        self.color_rect.update(left, top, width, width)

    def _update_color(self) -> None:
        # update cp_color
        self.color.r = self.rs.value
        self.color.g = self.gs.value
        self.color.b = self.bs.value

    def _apply_changes(self) -> None:
        if self.return_callback:
            out = self.color_to_tuple(self.color)
            self.return_callback(out)
        self.hide()
