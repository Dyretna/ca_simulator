# src/pygame_automata/ui/pygame_runner.py

"""
Pygame-based runner for 1D cellular automata simulations.

This module provides a real-time visual execution loop for CAEngine,
including UI controls for play, pause, single-step, fullscreen toggle,
and saving the final rendered generation. The design goal is to preserve
a continuous simulation flow while allowing the user to intervene only
after a CA run has completed.

Core behavior
-------------
The runner performs normal stepping every frame. A generation is drawn
immediately after it is produced by the CAEngine. The simulation continues
uninterrupted until the automaton reaches the bottom of the screen.

When the CA is finished (engine.needs_reset(...) becomes True), the runner
enters a post-simulation phase:

    1. A short delay (post_pause_ms) is applied.
    2. If a save was requested, the final CA image is written to disk.
    3. If the user has activated pause, the runner halts on the final frame.
       - No new CA is started.
       - No stepping occurs.
       - UI remains responsive and events are still processed.
       - The user may save the image while paused.
    4. If the user presses play, the CAEngine is reset and a new simulation
       begins immediately.

This design ensures that pausing never interrupts an active CA run.
Pause only applies *after* a simulation has completed, allowing the user
to inspect or save the final result without freezing the Pygame window.

UI controls
-----------
Play:
    Resets the CAEngine and starts a new simulation.

Pause:
    Freezes the runner only after a simulation has finished. Normal stepping
    continues during active CA execution.

Save:
    Sets a flag that causes the current CA image to be saved at the next
    safe point (either immediately after completion or during pause).

Controller and UIBar handle input dispatch and button rendering.
"""

from pathlib import Path

import pygame

from ..core.ca_engine import CAEngine
from ..core.rules import RulesetBase
from .pygame_ui import button as btn
from .pygame_ui.controller import Controller
from .pygame_ui.ui_bar import UIBar


class PygameRunner:
    def __init__(
        self,
        rulesetType: RulesetBase,
        ruleset_code: int,
        width: int = 1280,
        height: int = 720,
        cell_size: int = 4,
        in_order: bool = False,
        save_folder: str = "examples",
        post_pause_ms: int = 1000,
    ):
        pygame.init()

        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.save_folder = Path(save_folder)
        self.post_pause_ms = post_pause_ms

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("CA GUI Runner")
        self.clock = pygame.time.Clock()

        self.engine = CAEngine(
            rulesetType=rulesetType,
            ruleset_code=ruleset_code,
            width=width,
            cell_size=cell_size,
            in_order=in_order,
        )

        self.bg_color = (10, 20, 30)
        self.fill_color = (100, 130, 50)

        self.font = pygame.font.SysFont("consolas", 20)
        self.ui_height = 60
        self.ui_bar = UIBar(
            height=self.ui_height,
            bg_color=(20, 20, 30),
            text_color=(200, 200, 220),
            font=self.font,
        )
        self.ca_surface = pygame.Surface((width, height))
        self.controller = Controller(self, self.ui_bar)

        self._init_ui_buttons()

        self.running = True
        self.hard_pause = False
        self.save_flag = False

    def run(self):
        self.ca_surface.fill(self.bg_color)

        while self.running:
            for event in pygame.event.get():
                self.controller.handle(event)

            cells = self.engine.step()
            self._draw_generation(cells)

            # reset when  full
            if self.engine.needs_reset(self.height - self.ui_height):
                pygame.time.wait(self.post_pause_ms)
                if self.save_flag:
                    self.save()

                # pause button - after simulation
                if self.hard_pause:
                    self.screen.blit(self.ca_surface, (0, 0))
                    self.ui_bar.draw(self.screen, self.engine.ruleset_code)
                    pygame.display.flip()
                    self.clock.tick(60)

                    if self.save_flag:
                        self.save()
                    continue

                # play button -> reset sim
                self._reset_simulation()

            self.screen.blit(self.ca_surface, (0, 0))
            self.ui_bar.draw(self.screen, self.engine.ruleset_code)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    # --------------------------------------------
    # INIT HELPERS
    # --------------------------------------------
    def _init_ui_buttons(self):
        bg = (30, 40, 50)
        hover = (60, 60, 90)
        icon = (100, 130, 50)
        text = (230, 230, 230)

        self.ui_bar.add_button(
            btn.PlayButton(200, 10, 50, 40, bg, hover, icon, self.play)
        )
        self.ui_bar.add_button(
            btn.PauseButton(260, 10, 50, 40, bg, hover, icon, self.pause)
        )
        self.ui_bar.add_button(
            btn.TextButton(
                380, 10, 80, 40, "Save", self.font, bg, text, self.set_save_flag
            )
        )

    # --------------------------------------------
    # RENDER
    # --------------------------------------------

    def _draw_generation(self, cells):
        y = self.engine.generation * self.cell_size
        for i, cell in enumerate(cells):
            x = i * self.cell_size
            color = self.fill_color if cell == 1 else self.bg_color
            pygame.draw.rect(
                self.ca_surface, color, (x, y, self.cell_size, self.cell_size)
            )

    def _reset_simulation(self):
        new_rule = self.engine.reset()
        self.ca_surface.fill(self.bg_color)
        print(f"Current Rule: {new_rule}")

    # --------------------------------------------
    # CALLBACKS
    # --------------------------------------------

    def stop(self):
        self.running = False

    def play(self):
        self.hard_pause = False
        self._reset_simulation()

    def pause(self):
        self.hard_pause = True

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()

    def set_save_flag(self):
        self.save_flag = True

    def save(self):
        bit = self.engine.ruleset.bit_len
        rule_code = self.engine.ruleset_code

        self.save_folder.mkdir(parents=True, exist_ok=True)
        filename = self.save_folder / f"{bit}bit_rule_{rule_code}.png"

        pygame.image.save(self.ca_surface, filename)
        print(f"Saved {filename}")
        self.save_flag = False
