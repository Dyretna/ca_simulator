# src/pygame_automata/ui/pygame_ui/views/settings_screen.py
from typing import Optional

import pygame

from ...config import Config
from ...ui.theme import DEFAULT_FONT, SETTINGS_PANEL_BG, SETTINGS_TITLE_C, TITLE_FONT
from ..actions import Actions
from ..components import SettingsColumn, UIPanel


class SettingsScreen:
    def __init__(self, config: Config, actions: Actions):
        self.config = config
        self.actions = actions
        self.active = False

        # style and layout
        self.font = pygame.font.SysFont(**DEFAULT_FONT)
        self.title_font = pygame.font.SysFont(**TITLE_FONT)

        # panel
        self.panel = UIPanel()
        self.panel.place_bottom_buttons(self.font, self._apply_changes, self.hide)
        self.column: Optional[SettingsColumn] = None

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def show(self):
        """Activate settings screen."""
        self.active = True
        self.column = SettingsColumn(padding=self.panel.padding, row_height=40)
        self._build_column()

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
            local_pos = (event.pos[0] - self.panel.x, event.pos[1] - self.panel.y)
            self.column.handle_mouse_move(local_pos)
            self.panel.apply_button.on_mouse_move(event.pos)
            self.panel.cancel_button.on_mouse_move(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # translate positions from global to local
            local_pos = (event.pos[0] - self.panel.x, event.pos[1] - self.panel.y)
            self.column.handle_mouse_down(local_pos)
            self.panel.apply_button.on_mouse_down(event.pos)
            self.panel.cancel_button.on_mouse_down(event.pos)

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        # dark overlay - dim background
        w, h = surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # clear panel
        self.panel.surface.fill(SETTINGS_PANEL_BG)

        # Draw title and Options
        title = self.title_font.render("Settings", True, SETTINGS_TITLE_C)

        p = self.panel.padding
        title_height = title.get_height()
        column_offset_y = p + title_height + 20

        self.panel.surface.blit(title, (p, p))
        self.column.draw(self.panel.surface, column_offset_y)

        # blit panel
        surface.blit(self.panel.surface, (self.panel.x, self.panel.y))

        # draw bottom buttons
        self.panel.apply_button.draw(surface)
        self.panel.cancel_button.draw(surface)

    # ------------------------------------------------------------
    # Build helpers
    # ------------------------------------------------------------
    def _build_column(self):
        """Create TextButtonRow objects for each setting."""

        self.column.add_row(
            "Resolution",
            [(1280, 720), (1920, 1080)],
            lambda v: self.actions.set_resolution(*v),
            lambda v: v[0] == self.config.display.width
            and v[1] == self.config.display.height,
        )

        self.column.add_row(
            "Fullscreen",
            [True, False],
            lambda v: self.actions.set_fullscreen(v),
            lambda v: self.config.display.fullscreen == v,
        )

        self.column.add_row(
            "Ruleset Size",
            [8, 16, 32, 64],
            lambda v: self.actions.set_ruleset(v),
            lambda v: self.config.engine.bit_size == v,
        )

        self.column.add_row(
            "Cell Size",
            list(range(1, 11)),
            lambda v: self.actions.set_cellsize(v),
            lambda v: self.config.engine.cell_size == v,
        )

        self.column.add_row(
            "Random Mode",
            [True, False],
            lambda v: self.actions.set_random_mode(v),
            lambda v: self.config.engine.random_gen == v,
        )

        self.column.add_row(
            "AutoRun",
            [True, False],
            lambda v: self.actions.set_autorun(v),
            lambda v: self.config.general.auto_run == v,
        )

        self.column.add_row(
            "Info Overlay",
            [True, False],
            lambda v: self.actions.set_info(v),
            lambda v: self.config.general.show_info == v,
        )

    def _apply_changes(self):
        self.actions.update_settings()
        self.hide()
