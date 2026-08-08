# src/pygame_automata/ui/pygame_ui/ca_screen.py

import pygame


class CAScreen:
    """
    View responsible for drawing the CA surface and optional overlays.

    This view contains no simulation logic and no event handling.
    It simply renders the current CA generation and any non-modal
    overlays such as the rulebox.
    """

    def __init__(self, runner):
        """
        Parameters
        ----------
        runner : PygameRunner
            Reference to the main runner, used to access the CA surface
            and rulebox drawing helpers.
        """
        self.runner = runner

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the CA generation and any non-modal overlays.
        """
        # draw CA surface
        surface.blit(self.runner.ca_surface, (0, 0))

        # draw rulebox overlay if active
        if self.runner.show_rulebox:
            self.runner._draw_rulebox()
