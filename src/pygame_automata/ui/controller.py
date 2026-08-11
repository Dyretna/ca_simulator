# src/pygame_automata/ui/pygame_ui/controller.py

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from pygame_automata.pygame_runner import PygameRunner


class Controller:
    """
    Central input controller.

    Receives all pygame events and routes them to the active UI view.
    Keyboard input is interpreted as global runner controls.
    If the settings the settings view is active, the event is sent to its own
    handler that does global-to-local position calculations.
    """

    def __init__(self, runner: "PygameRunner"):
        """
        Parameters
        ----------
        runner : PygameRunner
            Reference to the main runner instance.
        """
        self.runner = runner
        self.config = runner.config

        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_down: bool = False

    def handle(self, event: pygame.event.Event) -> None:
        """
        Handle a single pygame event.

        Global events (QUIT, keyboard shortcuts) are handled directly.
        """

        if self.runner.settings_screen.is_active():
            if event.type == pygame.MOUSEMOTION:
                self.runner.settings_screen.handle_event(event)
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.runner.settings_screen.handle_event(event)
                return

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.runner.settings_screen.handle_event(event)
                return

            return

        if event.type == pygame.QUIT:
            self.runner.stop()
            return

        if event.type == pygame.KEYDOWN:
            self._handle_key(event.key)
            return

        if event.type == pygame.MOUSEMOTION:
            self.runner.ui_bar.handle_event(event)

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.runner.ui_bar.handle_event(event)

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.runner.stop()
        elif key == pygame.K_SPACE:
            self.runner.play()
        elif key == pygame.K_a:
            self.toggle_autorun()
        elif key == pygame.K_f:
            self.toggle_fullscreen()
        elif key == pygame.K_i:
            self.toggle_info()
        elif key == pygame.K_r:
            self.toggle_random_mode()
        elif key == pygame.K_s:
            self.toggle_save()

    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------
    def apply_changes(self):
        """Called from settings"""
        self.runner.update_settings()
        print("Display or Engine Updated")

    # --- Setters ---
    def set_resolution(self, w, h):
        self.config.display.width = w
        self.config.display.height = h

    def set_fullscreen(self, fs):
        self.config.display.fullscreen = fs

    def set_ruleset(self, b):
        self.config.engine.bit_size = b

    def set_cellsize(self, cs):
        self.config.engine.cell_size = cs

    def set_random_mode(self, m):
        self.config.engine.random_gen = m

    def set_autorun(self, ar):
        self.config.general.auto_run = ar

    def set_info(self, inf):
        self.config.general.show_info = inf

    # --- Toggles ---
    def toggle_save(self) -> None:
        "Save when CA simulation is done"
        self.save_flag = not self.save_flag

    def toggle_autorun(self) -> None:
        self.config.general.auto_run = not self.config.general.auto_run

    def toggle_fullscreen(self) -> None:
        self.config.display.fullscreen = not self.config.display.fullscreen
        res = (self.config.display.width, self.config.display.height)
        flags = pygame.FULLSCREEN if self.config.display.fullscreen else 0
        pygame.display.set_mode(res, flags)

    def toggle_info(self) -> None:
        """Toggle information overlay."""
        self.config.general.show_info = not self.config.general.show_info

    def toggle_random_mode(self) -> None:
        self.config.engine.random_gen = not self.config.engine.random_gen
        self.apply_changes()
