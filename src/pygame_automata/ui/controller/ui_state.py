# src/pygame_automata/ui/pygame_ui/controller/ui_state.py

import pygame


class UIState:
    """
    Simple UI view stack.

    Views are drawn in stack order (bottom to top). Input is routed to
    the top-most view.
    """

    def __init__(self):
        self._stack: list[object] = []

    def push(self, view: object) -> None:
        """Push a view on top of the UI stack."""
        self._stack.append(view)

    def pop(self) -> object | None:
        """Pop the top-most view from the stack."""
        if not self._stack:
            return None
        return self._stack.pop()

    def top(self) -> object | None:
        """Return the top-most view, or None if stack is empty."""
        if not self._stack:
            return None
        return self._stack[-1]

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw all views in stack order.

        Bottom-most view is drawn first, top-most last.
        """
        for view in self._stack:
            view.draw(surface)
