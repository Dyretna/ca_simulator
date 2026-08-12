from typing import TYPE_CHECKING, Callable, Tuple

import pygame

from ..components import Slider, TextButton
from ..theme import DEFAULT_FONT, SETTINGS_PANEL_BG, TITLE_FONT

if TYPE_CHECKING:
    from pygame_automata.pygame_runner import PygameRunner


ColorTuple = Tuple[int, int, int, int]


class ColorPicker:
    def __init__(self, runner: "PygameRunner"):
        self.runner = runner
        self.actions = runner.actions
        self.active: bool = False

        self.return_callback = None
        self.color = pygame.Color(0, 0, 0, 255)

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

        # buttons
        self.buttons: list[TextButton] = []
        self.apply_button: TextButton | None = None
        self.cancel_button: TextButton | None = None
        self.btn_w: int = 100
        self.btn_h: int = 40
        self.spacing: int = 20

        # set elements
        self.padding = 50

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

        self._build_panel()
        self._build_sliders()
        self._build_color_rect(self.padding + 10)
        self._build_apply_btn()
        self._build_cancel_btn()

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

        cp_local_x = event.pos[0] - self.surf_rect.x
        cp_local_y = event.pos[1] - self.surf_rect.y

        # Sliders gets all events
        for slider in self.sliders:
            lx = cp_local_x - slider.rect.x
            ly = cp_local_y - slider.rect.y
            slider.handle_event(event, lx, ly)

        # buttons: hover
        if event.type == pygame.MOUSEMOTION:
            self.apply_button.on_mouse_move((cp_local_x, cp_local_y))
            self.cancel_button.on_mouse_move((cp_local_x, cp_local_y))

        # buttons: click
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.apply_button.on_mouse_down((cp_local_x, cp_local_y))
            self.cancel_button.on_mouse_down((cp_local_x, cp_local_y))

    def draw(self, surface: pygame.Surface) -> None:
        self.cp_panel.fill(SETTINGS_PANEL_BG)
        self._update_color()

        rgb = (self.color.r, self.color.g, self.color.b)
        pygame.draw.rect(self.cp_panel, rgb, self.color_rect, border_radius=10)
        pygame.draw.rect(
            self.cp_panel, (0, 0, 0), self.color_rect, width=3, border_radius=10
        )

        [slider.draw(self.cp_panel) for slider in self.sliders]

        self.apply_button.draw(self.cp_panel)
        self.cancel_button.draw(self.cp_panel)

        screen_rect = surface.get_rect()
        self.surf_rect.center = screen_rect.center
        surface.blit(self.cp_panel, self.surf_rect)

    # --------------------------------------------------------------
    # private helpers
    # --------------------------------------------------------------

    def _build_panel(self):
        """Compute panel geometry."""
        w, h = pygame.display.get_window_size()
        self.panel_w = int(900)
        self.panel_h = int(350)
        self.panel_x = (w - self.panel_w) // 2
        self.panel_y = (h - self.panel_h) // 2

        self.cp_panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        self.surf_rect = self.cp_panel.get_rect()
        self.cp_panel.fill(SETTINGS_PANEL_BG)

    def _build_sliders(self):
        y_inc = 70
        self.rs.rect.topleft = (self.padding, self.padding)
        self.gs.rect.topleft = (self.padding, self.padding + y_inc)
        self.bs.rect.topleft = (self.padding, self.padding + y_inc * 2)

    def _build_color_rect(self, padding: int):
        width = 160
        left = self.surf_rect.width - (width + padding)
        top = padding
        self.color_rect.update(left, top, width, width)

    def _build_apply_btn(self):
        x_apply: int = self.panel_w - self.padding - self.btn_w * 2 - self.spacing
        y_btn: int = self.panel_h - self.padding - self.btn_h

        self.apply_button = TextButton(
            x_apply,
            y_btn,
            self.btn_w,
            self.btn_h,
            "Apply",
            self.font,
            self._apply_changes,
        )

    def _build_cancel_btn(self):
        x_cancel: int = self.panel_w - self.padding - self.btn_w
        y_btn: int = self.panel_h - self.padding - self.btn_h

        self.cancel_button = TextButton(
            x_cancel,
            y_btn,
            self.btn_w,
            self.btn_h,
            "Cancel",
            self.font,
            self.hide,
        )

    def _apply_changes(self) -> None:
        if self.return_callback:
            out = self.color_to_tuple(self.color)
            self.return_callback(out)
        self.hide()

    def _update_color(self) -> None:
        # update cp_color
        self.color.r = self.rs.value
        self.color.g = self.gs.value
        self.color.b = self.bs.value
