# src/pygame_automata/ui/pygame_ui/views/settings_screen.py
from dataclasses import dataclass
from typing import Optional

import pygame

from ....config import Config, DisplaySettings, EngineSettings, GeneralSettings
from ...actions import Actions
from ...components import SettingsColumn, UIPanel
from ...theme import DEFAULT_FONT, SETTINGS_PANEL_BG, SETTINGS_TITLE_C, TITLE_FONT
from .base import ModalView


@dataclass
class SettingsState:
    display: DisplaySettings
    general: GeneralSettings
    engine: EngineSettings


class SettingsScreen(ModalView):
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

    # show() in baseclass activates _on _show()
    def _on_show(self, **kwargs):
        self.local_state = self._state_from_config()
        self.column = SettingsColumn(padding=self.panel.padding, row_height=40)
        self._build_column()

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        self.draw_overlay(surface)

        # Prepare panel background with title on the panel.surface
        self.panel.surface.fill(SETTINGS_PANEL_BG)
        title = self.title_font.render("Settings", True, SETTINGS_TITLE_C)

        p = self.panel.padding
        title_height = title.get_height()
        column_offset_y = p + title_height + 20

        self.panel.surface.blit(title, (p, p))

        # blit panel BG with title to main surface
        surface.blit(self.panel.surface, (self.panel.x, self.panel.y))

        # compute global column origin and draw column using global coords
        global_column_y = self.panel.y + column_offset_y
        global_column_x = self.panel.x + self.panel.padding

        # pass both global X and Y to the column
        self.column.draw(surface, global_column_y, start_x=global_column_x)

        # draw bottom buttons
        self.panel.apply_button.draw(surface)
        self.panel.cancel_button.draw(surface)

    # ------------------------------------------------------------
    # Events
    # ------------------------------------------------------------

    def _handle_components(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.column.handle_mouse_move(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.column.handle_mouse_down(event.pos)

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
