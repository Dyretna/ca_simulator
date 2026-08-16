# src/pygame_automata/ui/pygame_ui/views/settings_screen.py

import pygame

from ...config import Config
from ...ui.theme import DEFAULT_FONT, SETTINGS_PANEL_BG, SETTINGS_TITLE_C, TITLE_FONT
from ..actions import Actions
from ..components import SettingsColumn, TextButton


class SettingsScreen:
    def __init__(self, config: Config, actions: Actions):
        self.config = config
        self.actions = actions
        self.active = False

        self.font = pygame.font.SysFont(**DEFAULT_FONT)
        self.title_font = pygame.font.SysFont(**TITLE_FONT)

        self.column: SettingsColumn = None
        self.settings_panel = None
        self.panel_x = 0
        self.panel_y = 0
        self.panel_w = 0
        self.panel_h = 0

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def show(self):
        """Activate settings screen."""
        self.active = True
        self._build_panel()
        self.column = self._build_column()
        self._build_apply_btn()
        self._build_cancel_btn()

    def hide(self):
        """Deactivate settings screen."""
        self.active = False

    def is_active(self):
        return self.active

    def handle_event(self, event: pygame.event.Event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return

        if event.type == pygame.MOUSEMOTION:
            # translate positions from global to local
            local_pos = (event.pos[0] - self.panel_x, event.pos[1] - self.panel_y)

            self.column.handle_mouse_move(local_pos)

            self.apply_button.on_mouse_move(event.pos)
            self.cancel_button.on_mouse_move(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # translate positions from global to local
            local_pos = (event.pos[0] - self.panel_x, event.pos[1] - self.panel_y)

            self.column.handle_mouse_down(local_pos)

            self.apply_button.on_mouse_down(event.pos)
            self.cancel_button.on_mouse_down(event.pos)

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        # dark overlay - dim background
        w, h = surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # clear panel
        self.settings_panel.fill(SETTINGS_PANEL_BG)

        # title
        title = self.title_font.render("Settings", True, SETTINGS_TITLE_C)
        self.settings_panel.blit(title, (20, 20))

        # Draw options row
        self.column.draw(self.settings_panel)

        # blit panel
        surface.blit(self.settings_panel, (self.panel_x, self.panel_y))

        # draw bottom buttons
        self.apply_button.draw(surface)
        self.cancel_button.draw(surface)

    # ------------------------------------------------------------
    # Build helpers
    # ------------------------------------------------------------
    def _build_panel(self):
        """Compute panel geometry."""
        w, h = pygame.display.get_window_size()
        self.panel_w = int(w * 0.6)
        self.panel_h = int(h * 0.6)
        self.panel_x = (w - self.panel_w) // 2
        self.panel_y = (h - self.panel_h) // 2

        self.settings_panel = pygame.Surface(
            (self.panel_w, self.panel_h), pygame.SRCALPHA
        )
        self.settings_panel.fill(SETTINGS_PANEL_BG)

    def _build_column(self):
        """Create TextButtonRow objects for each setting."""
        col = SettingsColumn(padding=80, row_height=40)

        col.add_row(
            "Resolution",
            [(1280, 720), (1920, 1080)],
            lambda v: self.actions.set_resolution(*v),
            lambda v: v[0] == self.config.display.width
            and v[1] == self.config.display.height,
        )

        col.add_row(
            "Fullscreen",
            [True, False],
            lambda v: self.actions.set_fullscreen(v),
            lambda v: self.config.display.fullscreen == v,
        )

        col.add_row(
            "Ruleset Size",
            [8, 16, 32, 64],
            lambda v: self.actions.set_ruleset(v),
            lambda v: self.config.engine.bit_size == v,
        )

        col.add_row(
            "Cell Size",
            list(range(1, 11)),
            lambda v: self.actions.set_cellsize(v),
            lambda v: self.config.engine.cell_size == v,
        )

        col.add_row(
            "Random Mode",
            [True, False],
            lambda v: self.actions.set_random_mode(v),
            lambda v: self.config.engine.random_gen == v,
        )

        col.add_row(
            "AutoRun",
            [True, False],
            lambda v: self.actions.set_autorun(v),
            lambda v: self.config.general.auto_run == v,
        )

        col.add_row(
            "Info Overlay",
            [True, False],
            lambda v: self.actions.set_info(v),
            lambda v: self.config.general.show_info == v,
        )

        return col

    def _build_apply_btn(self):
        btn_y = self.panel_y + self.panel_h - 60

        self.apply_button = TextButton(
            self.panel_x + self.panel_w - 220,
            btn_y,
            100,
            40,
            "Apply",
            self.font,
            self._apply_changes,
        )

    def _build_cancel_btn(self):
        btn_y = self.panel_y + self.panel_h - 60
        self.cancel_button = TextButton(
            self.panel_x + self.panel_w - 110,
            btn_y,
            100,
            40,
            "Cancel",
            self.font,
            self.hide,
        )

    def _apply_changes(self):
        self.actions.update_settings()
        self.hide()
