# src/pygame_automata/ui/pygame_ui/views/settings_screen.py
from dataclasses import dataclass
from typing import Optional

import pygame

from ...config import Config, DisplaySettings, EngineSettings, GeneralSettings
from ...ui.theme import DEFAULT_FONT, SETTINGS_PANEL_BG, SETTINGS_TITLE_C, TITLE_FONT
from ..actions import Actions
from ..components import SettingsColumn, UIPanel


@dataclass
class SettingsState:
    display: DisplaySettings
    general: GeneralSettings
    engine: EngineSettings


class SettingsScreen:
    """
    Modal view for editing simulator configuration.

    SettingsScreen presents a centered panel with labelled setting rows and
    Apply/Cancel controls. When opened, it creates a local SettingsState
    snapshot from the global Config. User interactions modify this local
    state only; no changes are applied to the simulator until Apply is
    pressed. Cancel discards the local state and closes the view.

    The screen manages its own active flag, builds a SettingsColumn on
    show(), and routes mouse/keyboard events to its components. A dimmed
    overlay is drawn behind the panel while active.
    """

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

        # local state updates when opening
        self.local_state: Optional[SettingsState] = None

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def show(self):
        """Activate settings screen."""
        self.active = True
        self.local_state = self._state_from_config()
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
            lambda v: self._set_local("display", "width", v[0])
            or self._set_local("display", "height", v[1]),
            lambda v: (
                self.local_state.display.width == v[0]
                and self.local_state.display.height == v[1]
            ),
        )

        self.column.add_row(
            "Fullscreen",
            [True, False],
            lambda v: self._set_local("display", "fullscreen", v),
            lambda v: self.local_state.display.fullscreen == v,
        )

        self.column.add_row(
            "Ruleset Size",
            [8, 16, 32, 64],
            lambda v: self._set_local("engine", "bit_size", v),
            lambda v: self.local_state.engine.bit_size == v,
        )

        self.column.add_row(
            "Cell Size",
            list(range(1, 11)),
            lambda v: self._set_local("engine", "cell_size", v),
            lambda v: self.local_state.engine.cell_size == v,
        )

        self.column.add_row(
            "Random Mode",
            [True, False],
            lambda v: self._set_local("engine", "random_gen", v),
            lambda v: self.local_state.engine.random_gen == v,
        )

        self.column.add_row(
            "AutoRun",
            [True, False],
            lambda v: self._set_local("general", "auto_run", v),
            lambda v: self.local_state.general.auto_run == v,
        )

    # -----------------------------------------------------------------
    # Set State and Apply
    # -----------------------------------------------------------------

    def _state_from_config(self):
        return SettingsState(
            display=DisplaySettings(
                width=self.config.display.width,
                height=self.config.display.height,
                fullscreen=self.config.display.fullscreen,
            ),
            general=GeneralSettings(
                auto_run=self.config.general.auto_run,
                idle_pause_ms=self.config.general.idle_pause_ms,
            ),
            engine=EngineSettings(
                bit_size=self.config.engine.bit_size,
                cell_size=self.config.engine.cell_size,
                random_gen=self.config.engine.random_gen,
            ),
        )

    def state_to_config(self):
        # display
        self.config.display.width = self.local_state.display.width
        self.config.display.height = self.local_state.display.height
        self.config.display.fullscreen = self.local_state.display.fullscreen

        # general
        self.config.general.auto_run = self.local_state.general.auto_run
        self.config.general.idle_pause_ms = self.local_state.general.idle_pause_ms

        # engine
        self.config.engine.bit_size = self.local_state.engine.bit_size
        self.config.engine.cell_size = self.local_state.engine.cell_size
        self.config.engine.random_gen = self.local_state.engine.random_gen

    def _set_local(self, section: str, key: str, value):
        setattr(getattr(self.local_state, section), key, value)

    def _apply_changes(self):
        self.state_to_config()
        self.actions.update_settings()
        self.hide()
