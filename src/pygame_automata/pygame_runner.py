# src/pygame_automata/ui/pygame_runner.py

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

import pygame

from pygame_automata.config import Config
from pygame_automata.core.ca_engine import CAEngine
from pygame_automata.ui.actions import Actions
from pygame_automata.ui.controller import Controller
from pygame_automata.ui.theme import DEFAULT_FONT
from pygame_automata.ui.views.colorpicker import ColorPicker
from pygame_automata.ui.views.settings_screen import SettingsScreen
from pygame_automata.ui.views.ui_bar import UIBar


class PygameRunner:
    """
    Main pygame-based runner for the CAEngine.
    """

    def __init__(self):
        """
        Parameters
        ----------
        config : Config
            Configuration object providing initial width, height,
            cell_size, ruleset, and other parameters.
        """
        pygame.init()
        pygame.display.set_caption("Cellular Automata")

        # resolve paths
        self.config = Config()

        # timing
        self.clock = pygame.time.Clock()
        self.running = False

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
        self.controller = Controller(self)

        self.save_flag = False

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Main execution loop."""

        self.running = True
        self.ca_surface.fill(self.config.colors.ca_bg_color)
        print(f"Ruleset Bitsize: {self.config.engine.bit_size}")
        print(f"First Rule: {self.ruleset_code}")

        # first draw before fullscreen
        self.screen.blit(self.ca_surface, (0, 0))
        self.ui_bar.draw(self.screen)
        pygame.display.flip()

        while self.running:
            # INPUT
            for event in pygame.event.get():
                self.controller.handle(event)

            # SIMULATION always runs unless settings is open
            if not self.settings_screen.is_active() or self.colorpicker.is_active():
                # normal step
                cells = self.engine.step()
                self._draw_generation(cells)

                # reset when full
                if self.engine.simulation_done(self.config.display.height):
                    if self._handle_post_sim():
                        # autorun OFF -> freeze on final frame
                        continue

            # draw ui and settings
            self._draw_ui_frame()
            self.clock.tick(60)

        print("Exiting...")
        pygame.quit()

    def play(self):
        """Plays next or resets the simulation"""
        self._reset_simulation()

    def stop(self) -> None:
        """Stop the main loop."""
        self.running = False

    # --- Settings ---

    def update_settings(self) -> None:
        """
        Rebuild engine and surfaces after settings change.
        """
        self.engine = CAEngine(
            width=self.config.display.width,
            cell_size=self.config.engine.cell_size,
            bit_size=self.config.engine.bit_size,
            ruleset_code=self.ruleset_code,
            random=self.config.engine.random_gen,
        )
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
    # Render
    # ------------------------------------------------------------------

    def _draw_generation(self, cells) -> None:
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

    def _handle_post_sim(self):
        end = pygame.time.get_ticks() + self.config.engine.post_sim_pause_ms

        # autorun OFF -> freeze on final frame only
        if not self.config.general.auto_run:
            while pygame.time.get_ticks() < end:
                for event in pygame.event.get():
                    self.controller.handle(event)
                self._draw_ui_frame()
                self.clock.tick(60)
                if self.save_flag:
                    self._save()
            return

        # autorun ON -> pause, then save, then reset
        while pygame.time.get_ticks() < end:
            for event in pygame.event.get():
                self.controller.handle(event)
            self._draw_ui_frame()
            self.clock.tick(60)
            if self.save_flag:
                self._save()

        self._reset_simulation()

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
    # initialize, reset, save
    # --------------------------------------------------------

    def _initialize_pygame(self):
        # recreate display
        res = (self.config.display.width, self.config.display.height)
        flags = pygame.FULLSCREEN if self.config.display.fullscreen else 0
        self.screen = pygame.display.set_mode(res, flags)

        # recreate CA surface
        self.ca_surface = pygame.Surface(res)
        self.ca_surface.fill(self.config.colors.ca_bg_color)

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
