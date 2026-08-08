# src/pygame_automata/ui/pygame_ui/controller/controller.py

from typing import TYPE_CHECKING

import pygame

from .ui_state import UIState

if TYPE_CHECKING:
    from pygame_automata.pygame_runner import PygameRunner


class Controller:
    """
    Central input controller.

    Receives all pygame events and routes them to the active UI view.
    Keyboard input is interpreted as global runner controls, while
    mouse input is forwarded to the top-most view in the UIState stack.
    """

    def __init__(self, runner: "PygameRunner", ui_state: UIState):
        """
        Parameters
        ----------
        runner : PygameRunner
            Reference to the main runner instance.
        ui_state : UIState
            UI view stack used for routing input and drawing.
        """
        self.runner = runner
        self.ui_state = ui_state

        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_down: bool = False

    def handle(self, event: pygame.event.Event) -> None:
        """
        Handle a single pygame event.

        Global events (QUIT, keyboard shortcuts) are handled directly.
        Mouse events are forwarded to the top-most view in the UI stack.
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

        # route mouse events to active view
        active_view = self.ui_state.top()
        if active_view is None:
            return

        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            if hasattr(active_view, "handle_event"):
                active_view.handle_event(event)
            return

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.mouse_down = False

            if hasattr(active_view, "handle_event"):
                active_view.handle_event(event)

    def _handle_key(self, key: int) -> None:
        """
        Interpret keyboard input and control the runner.

        ESC stops the runner, SPACE toggles pause, S saves the current
        CA image, F toggles fullscreen, and D toggles the rulebox overlay.
        """
        if key == pygame.K_ESCAPE:
            self.runner.stop()
        elif key == pygame.K_SPACE:
            self.runner.toggle_pause()
        elif key == pygame.K_s:
            self.runner.save()
        elif key == pygame.K_f:
            self.runner.toggle_fullscreen()
        elif key == pygame.K_d:
            self.runner.toggle_rulebox()
