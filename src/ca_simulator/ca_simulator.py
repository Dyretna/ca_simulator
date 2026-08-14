# src/pygame_automata/ca_simulator.py

"""
Pygame-based runner for interactive 1D cellular automata simulations.

This module manages the real-time execution loop, rendering, and UI
controls for CAEngine. It provides a continuous simulation flow where
each generation is drawn immediately as it is produced. When the
automaton reaches the bottom of the screen, the runner enters a
post-simulation phase that allows saving, pausing, or restarting the
simulation without interrupting an active run.

The runner also supports a settings overlay (SettingsScreen)
that allows the user to modify core configuration parameters such as
resolution, bit-size, cell size, and update mode. When the settings
screen is active, the normal simulation loop is suspended visually and
all input events are routed to the settings UI. Once the user confirms
changes, the runner rebuilds its CAEngine and Pygame surfaces via
update_settings(), ensuring that the new configuration takes effect
before resuming normal execution.
"""

import os
from enum import Enum, auto

import pygame

from .config import Config
from .core.ca_engine import CAEngine
from .ui.actions import Actions
from .ui.theme import DEFAULT_FONT
from .ui.views.colorpicker import ColorPicker
from .ui.views.settings_screen import SettingsScreen
from .ui.views.ui_bar import UIBar


class RunState(Enum):
    INITIALIZATION = auto()
    RUNNING = auto()
    IDLE = auto()
    RESET = auto()
    QUIT = auto()


class CASimulator:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cellular Automata")

        # resolve paths
        self.config = Config()
        self.state = RunState.INITIALIZATION
        rows = [(f"{k:<8} : {v}") for k, v in self.config.__dict__.items()]
        rows.insert(0, "INITIALIZATION")
        print("\n\t- ".join(rows), "\n")

        # timing
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.idle_pause_ms = self.config.general.idle_pause_ms
        self.idle_end = 0

        # core engine
        self.ruleset_code: int = 30

        self.engine = CAEngine(
            bit_size=self.config.engine.bit_size,
            ruleset_code=self.ruleset_code,
            width=self.config.display.width,
            cell_size=self.config.engine.cell_size,
            random=self.config.engine.random_gen,
        )

        self._initialize_pygame()

        self.actions = Actions(self)
        self.settings_screen = SettingsScreen(self)
        self.colorpicker = ColorPicker(self)
        self.ui_bar = UIBar(self)

        self.save_flag = False
        self.display_changes = False

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Main execution loop."""

        # self state is running
        self._set_state(RunState.RUNNING)
        self.ca_surface.fill(self.config.colors.ca_bg_color)
        print(f"Ruleset Bitsize: {self.config.engine.bit_size}")
        print(f"First Rule: {self.ruleset_code}")

        # first draw before fullscreen
        self.screen.blit(self.ca_surface, (0, 0))
        self.ui_bar.draw(self.screen)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                self._handle_event(event)

            match self.state:
                case RunState.RUNNING:
                    # SIMULATION runs unless settings or colorpicker is open
                    if (
                        not self.settings_screen.is_active()
                        and not self.colorpicker.is_active()
                    ):
                        # normal step
                        cells = self.engine.step()
                        self._step(cells)

                        # set State to idle
                        if self.engine.simulation_done(self.config.display.height):
                            self.idle_end = pygame.time.get_ticks() + self.idle_pause_ms
                            self._set_state(RunState.IDLE)

                case RunState.IDLE:
                    # If Autorun is active,
                    # set to reset after short break
                    if self.save_flag:
                        self._save()

                    if pygame.time.get_ticks() >= self.idle_end:
                        if self.config.general.auto_run:
                            self._set_state(RunState.RESET)

                case RunState.RESET:
                    self._reset_simulation()
                    self._set_state(RunState.RUNNING)

                case RunState.QUIT:
                    print("Exiting...")
                    pygame.quit()
                    return

            # always draw UI and tick
            self._draw_ui_frame()
            self.clock.tick(self.fps)

    # ------------------------------------------------------------------
    # Public API - reached by Actions
    # ------------------------------------------------------------------

    def play(self):
        """Plays next or resets the simulation"""
        self._set_state(RunState.RESET)

    def quit(self) -> None:
        """Stops the main loop, which quits Pygame."""
        self._set_state(RunState.QUIT)

    # --- Settings ---

    def update_settings(self) -> None:
        """Rebuild engine and surfaces after settings change."""
        self.engine = CAEngine(
            width=self.config.display.width,
            cell_size=self.config.engine.cell_size,
            bit_size=self.config.engine.bit_size,
            ruleset_code=self.ruleset_code,
            random=self.config.engine.random_gen,
        )
        if self.display_changes:
            self._initialize_pygame()
        self.ui_bar.rebuild()

    def settings_is_active(self):
        return self.settings_screen.is_active()

    def open_settings(self) -> None:
        """Show the settings screen as a modal view."""
        if not self.settings_is_active():
            self.settings_screen.show()

    def close_settings(self) -> None:
        """Hide the settings screen"""
        if not self.settings_is_active():
            return
        self.settings_screen.hide()

    # --- ColorPicker ---

    def colorpicker_is_active(self):
        return self.colorpicker.is_active()

    def open_colorpicker(self) -> None:
        if not self.colorpicker_is_active():
            self.colorpicker.show()

    def close_colorpicker(self) -> None:
        if not self.colorpicker_is_active():
            return
        self.colorpicker.hide()

    # toggle fullscreen
    def toggle_fullscreen(self) -> None:
        self.config.display.fullscreen = not self.config.display.fullscreen
        res = (self.config.display.width, self.config.display.height)
        flags = pygame.FULLSCREEN if self.config.display.fullscreen else 0
        pygame.display.set_mode(res, flags)

    # ------------------------------------------------------------------
    # FLow Control
    # ------------------------------------------------------------------

    def _handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle a single pygame event.

        Route to active modal view. If no view is active, route to UIbar.
        Global events (QUIT, keyboard shortcuts) are handled directly.
        """
        if event.type == pygame.QUIT:
            self.quit()
            return

        elif self.settings_screen.is_active():
            self.settings_screen.handle_event(event)
            return

        elif self.colorpicker.is_active():
            self.colorpicker.handle_event(event)

        else:
            self.ui_bar.handle_event(event)
            return

    def _set_state(self, state: RunState):
        print(f"Transitioning from {self.state.name} to {state.name}..")
        self.state = state

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def _step(self, cells) -> None:
        """Draw one CA generation row onto the CA surface."""

        y = self.engine.generation * self.engine.cell_size
        width = self.config.display.width

        for i, cell in enumerate(cells):
            x = i * self.engine.cell_size
            if x >= width:
                break

            color = (
                self.config.colors.ca_fg_color
                if cell == 1
                else self.config.colors.ca_bg_color
            )
            pygame.draw.rect(
                self.ca_surface,
                color,
                (x, y, self.engine.cell_size, self.engine.cell_size),
            )

    def _draw_ui_frame(self):
        self.screen.blit(self.ca_surface, (0, 0))
        self.ui_bar.draw(self.screen)
        if self.config.general.show_info:
            self._draw_info()
        if self.settings_screen.is_active():
            self.settings_screen.draw(self.screen)
        if self.colorpicker.is_active():
            self.colorpicker.draw(self.screen)
        pygame.display.flip()

    def _draw_info(self) -> None:
        """Draw the info overlay on top of the CA surface."""

        font = pygame.font.SysFont(**DEFAULT_FONT)

        bit_str = f"{self.ruleset_code:0{self.engine.ruleset.bit_size}b}"
        grouped = " ".join(bit_str[i : i + 8] for i in range(0, len(bit_str), 8))
        text_str = f"Rule: {self.engine.ruleset_code} ({grouped})"
        text = font.render(text_str, True, (255, 255, 255))

        text_w, text_h = font.size(text_str)
        padding = 10
        box_w = text_w + padding * 2
        box_h = text_h + padding

        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 120))
        self.screen.blit(box, (0, 0))
        self.screen.blit(text, (padding, padding // 2))

    # --------------------------------------------------------
    # Initialize, Reset, Save
    # --------------------------------------------------------

    def _initialize_pygame(self) -> None:
        # recreate display
        res = (self.config.display.width, self.config.display.height)
        flags = pygame.FULLSCREEN if self.config.display.fullscreen else 0
        self.screen = pygame.display.set_mode(res, flags)

        # recreate CA surface
        self.ca_surface = pygame.Surface(res)
        self.ca_surface.fill(self.config.colors.ca_bg_color)

        # reset flag if updating
        self.display_changes = False

    def _reset_simulation(self) -> None:
        """Reset CA simulation to initial state."""

        new_rule = self.engine.reset()
        self.ruleset_code = new_rule
        self.ca_surface.fill(self.config.colors.ca_bg_color)
        print(f"Current Rule: {new_rule}")

    def _save(self) -> None:
        """Save the current CA surface as an image."""

        filename = f"{self.engine.ruleset.bit_size}bit_rule{self.ruleset_code}.png"
        path = os.path.join(self.config.paths.output_dir, filename)
        pygame.image.save(self.ca_surface, path)
        print(f"Saved CA image to {path}")
        self.save_flag = False
