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

from pygame_automata.config import EngineConfig
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

    def __init__(self, engine_config: EngineConfig):
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
        self.assets_dir = getattr(engine_config, "assets_dir", "assets")
        self.output_dir = getattr(engine_config, "output_dir", "examples")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)

        # core dimensions / settings
        self.width = engine_config.width
        self.height = engine_config.height
        self.cell_size = engine_config.cell_size

        # timing
        self.clock = pygame.time.Clock()
        self.running = False

        if hasattr(engine_config, "engine_config"):
            self.post_pause_ms = engine_config.pause_sec
        else:
            self.post_pause_ms = 500

        # flags / state
        self.show_rulebox = False
        self.save_flag = False
        self.hard_pause = False
        self.in_order = engine_config.in_order

        # core engine
        self.ruleset: RulesetBase = get_ruleset(engine_config.bit_size)
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

        self.fullscreen = engine_config.fullscreen
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
                cells = self.engine.step()
                self._draw_generation(cells)

                # reset when full
                if self.engine.needs_reset(self.height):
                    pygame.time.wait(self.post_pause_ms)
                    if self.save_flag:
                        self._save()

                    # PAUSE: freeze final frame
                    if self.hard_pause:
                        self.screen.blit(self.ca_surface, (0, 0))
                        self.ui_bar.draw(self.screen)
                        pygame.display.flip()
                        self.clock.tick(60)

                        if self.save_flag:
                            self._save()
                        continue

                    # NO PAUSE: start next simulation
                    self._reset_simulation()

            # draw ui and settings
            self.screen.blit(self.ca_surface, (0, 0))
            self.ui_bar.draw(self.screen)

            if self.settings_screen.is_active():
                self.settings_screen.draw(self.screen)

            pygame.display.flip()

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

    def save(self) -> None:
        "Save when CA simulation is done"
        self.save_flag = True

    def toggle_pause(self) -> None:
        """Toggle simulation pause."""
        self.hard_pause = not self.hard_pause

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

    def _initialize_pygame(self):
        # recreate display
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((self.width, self.height), flags)

        # recreate CA surface
        self.ca_surface = pygame.Surface((self.width, self.height))
        self.ca_surface.fill(self.ca_bg_color)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

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
        # Example placeholder; replace with your actual rulebox drawing:
        font = pygame.font.SysFont("consolas", 18)
        txt = font.render(f"Ruleset: {self.engine.ruleset}", True, (200, 200, 200))
        box = pygame.Surface((txt.get_width() + 20, txt.get_height() + 12))
        box.fill((20, 20, 20))
        box.blit(txt, (10, 6))
        self.ca_surface.blit(box, (10, 10))

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
