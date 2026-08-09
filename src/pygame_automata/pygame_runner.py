# src/pygame_automata/ui/pygame_runner.py

"""
Pygame-based runner for interactive 1D cellular automata simulations.

This module manages the real-time execution loop, rendering, and UI
controls for CAEngine. It provides a continuous simulation flow where
each generation is drawn immediately as it is produced. When the
automaton reaches the bottom of the screen, the runner enters a
post-simulation phase that allows saving, pausing, or restarting the
simulation without interrupting an active run.

The runner also supports a fullscreen settings overlay (SettingsScreen)
that allows the user to modify core configuration parameters such as
resolution, bit-size, cell size, and update mode. When the settings
screen is active, the normal simulation loop is suspended visually and
all input events are routed to the settings UI. Once the user confirms
changes, the runner rebuilds its CAEngine and Pygame surfaces via
update_settings(), ensuring that the new configuration takes effect
before resuming normal execution.
"""

# src/pygame_automata/ui/pygame_ui/pygame_runner.py

import os

import pygame

from pygame_automata.config import Config
from pygame_automata.core.ca_engine import CAEngine
from pygame_automata.core.rules import RulesetBase, get_ruleset
from pygame_automata.ui.controller import Controller
from pygame_automata.ui.theme import CA_BG_COLOR, CA_FILL_COLOR
from pygame_automata.ui.views.ca_screen import CAScreen
from pygame_automata.ui.views.settings_screen import SettingsScreen
from pygame_automata.ui.views.ui_bar import UIBar


class PygameRunner:
    """
    Main pygame-based runner for the CAEngine.
    """

    def __init__(self, config: Config):
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
        self.assets_dir = config.assets_dir
        self.output_dir = config.output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)

        # core dimensions / settings
        self.width = config.width
        self.height = config.height
        self.cell_size = config.cell_size

        # timing
        self.clock = pygame.time.Clock()
        self.running = False
        self.post_sim_pause_ms = config.post_sim_pause_ms

        # flags / state
        self.show_rulebox = False
        self.save_flag = False
        self.auto_run = False
        self.in_order = False

        # core engine
        self.ruleset: RulesetBase = get_ruleset(config.bit_size)
        self.ruleset_code: int = 30

        self.engine = CAEngine(
            ruleset=self.ruleset,
            ruleset_code=self.ruleset_code,
            width=self.width,
            cell_size=self.cell_size,
            in_order=self.in_order,
        )

        self.ca_bg_color = CA_BG_COLOR
        self.ca_fill_color = CA_FILL_COLOR

        self.fullscreen = config.fullscreen
        self._initialize_pygame()

        # views
        self.ca_screen = CAScreen(self)
        self.ui_bar = UIBar(self)
        self.settings_screen = SettingsScreen(self)

        # controller
        self.controller = Controller(self)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """
        Main execution loop.

        Draws all views via UIState, routes input via Controller, and
        steps the simulation only when the runner is not in hard pause mode.
        """

        self.running = True
        self.ca_surface.fill(self.ca_bg_color)
        print(f"Ruleset Bitsize: {self.ruleset.bit_size}")
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
            if not self.settings_screen.is_active():
                # normal step
                cells = self.engine.step()
                self._draw_generation(cells)

                # reset when full
                if self.engine.needs_reset(self.height):
                    if self._handle_post_sim():
                        # autorun OFF -> freeze on final frame
                        continue

            # draw ui and settings
            self._draw_ui_frame()
            self.clock.tick(60)

        print("Exiting...")
        pygame.quit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def play(self):
        """Plays next or resets the simulation"""
        self._reset_simulation()

    def stop(self) -> None:
        """Stop the main loop."""
        self.running = False

    def toggle_save(self) -> None:
        "Save when CA simulation is done"
        print("in toggle save")
        self.save_flag = not self.save_flag
        print(self.save_flag)

    def toggle_autorun(self) -> None:
        """Toggle simulation pause."""
        self.auto_run = not self.auto_run

    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        self.fullscreen = not self.fullscreen
        pygame.display.toggle_fullscreen()

    def toggle_rulebox(self) -> None:
        """Toggle rulebox overlay."""
        self.show_rulebox = not self.show_rulebox

    # --- settings ---
    def open_settings(self) -> None:
        """Show the settings screen as a modal view."""
        if self.settings_screen.is_active():
            return
        self.settings_screen.show()

    def close_settings(self) -> None:
        """Hide the settings screen and remove it from the UI stack."""
        if not self.settings_screen.is_active():
            return
        self.settings_screen.hide()

    def update_settings(self) -> None:
        """
        Rebuild engine and surfaces after settings change.

        Called by SettingsScreen._apply_changes().
        """
        # update engine based on runner attributes
        self.ruleset = get_ruleset(self.bit_size)
        self.engine = CAEngine(
            width=self.width,
            cell_size=self.cell_size,
            ruleset=self.ruleset,
            ruleset_code=self.ruleset_code,
            in_order=self.in_order,
        )

        self._initialize_pygame()
        self.ui_bar = UIBar(self)
        self.controller = Controller(self)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _draw_ui_frame(self):
        self.screen.blit(self.ca_surface, (0, 0))
        self.ui_bar.draw(self.screen)
        if self.show_rulebox:
            self._draw_rulebox()
        if self.settings_screen.is_active():
            self.settings_screen.draw(self.screen)
        pygame.display.flip()

    def _handle_post_sim(self):
        end = pygame.time.get_ticks() + self.post_sim_pause_ms

        # autorun OFF -> freeze on final frame only
        if not self.auto_run:
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

    def _draw_generation(self, cells) -> None:
        """Draw one CA generation row onto the CA surface."""

        y = self.engine.generation * self.cell_size
        width = self.width

        for i, cell in enumerate(cells):
            x = i * self.cell_size
            if x >= width:
                break

            color = self.ca_fill_color if cell == 1 else self.ca_bg_color

            pygame.draw.rect(
                self.ca_surface, color, (x, y, self.cell_size, self.cell_size)
            )

    def _initialize_pygame(self):
        # recreate display
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((self.width, self.height), flags)

        # recreate CA surface
        self.ca_surface = pygame.Surface((self.width, self.height))
        self.ca_surface.fill(self.ca_bg_color)

    def _reset_simulation(self) -> None:
        """
        Reset CA simulation to initial state.

        Delegates to CAEngine.reset() and clears the CA surface.
        """
        new_rule = self.engine.reset()
        self.ruleset_code = new_rule
        self.ca_surface.fill(self.ca_bg_color)
        print(f"Current Rule: {new_rule}")

    def _draw_rulebox(self) -> None:
        """
        Draw the rulebox overlay on top of the CA surface.

        This is called by CAScreen when `show_rulebox` is True.
        """
        font = pygame.font.SysFont("consolas", 20)

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

    def _save(self) -> None:
        """
        Save the current CA surface as an image.

        Uses a timestamp-based filename in the configured output directory.
        """
        filename = f"{self.engine.ruleset.bit_size}bit_rule{self.ruleset_code}.png"
        path = os.path.join(self.output_dir, filename)
        pygame.image.save(self.ca_surface, path)
        print(f"Saved CA image to {path}")
        self.save_flag = False
