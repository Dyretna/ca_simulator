# src/pygame_automata/ui/pygame_ui/controller.py

import pygame


class Controller:
    """
    Central input controller.

    Receives all pygame events and:
    - interprets keyboard input and controls the runner
    - forwards mouse input to the UI bar
    """

    def __init__(self, runner, ui_bar):
        """
        Parameters
        ----------
        param runner : PygameRunner instance
        param ui_bar : BottomBar instance
        """
        self.runner = runner
        self.ui_bar = ui_bar

        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_down: bool = False

    def handle(self, event: pygame.event.Event):
        """Handle a single pygame event."""

        if event.type == pygame.QUIT:
            self.runner.stop()
            return

        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            self.ui_bar.on_mouse_move(event.pos)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_down = True
                self.ui_bar.on_mouse_down(event.pos)
            return

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_down = False
                self.ui_bar.on_mouse_up(event.pos)
            return

        if event.type == pygame.KEYDOWN:
            self._handle_key(event.key)

    def _handle_key(self, key: int):
        """Interpret keyboard input and control the runner."""

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
