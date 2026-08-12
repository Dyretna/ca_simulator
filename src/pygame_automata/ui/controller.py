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
        self.settings_screen = runner.settings_screen
        self.ui_bar = runner.ui_bar

    def handle(self, event: pygame.event.Event) -> None:
        """
        Handle a single pygame event.

        Global events (QUIT, keyboard shortcuts) are handled directly.
        """

        if self.settings_screen.is_active():
            self.settings_screen.handle_event(event)
            return

        elif event.type == pygame.QUIT:
            self.runner.actions.stop()
            return

        else:
            self.ui_bar.handle_event(event)
            return
