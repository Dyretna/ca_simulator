from abc import ABC, abstractmethod
from typing import Optional

import pygame

from ...components import UIPanel


class ModalView(ABC):
    """Contract for modal views."""

    def __init__(self):
        self.active: bool = False
        self.panel: Optional[UIPanel] = None

    def show(self, **kwargs) -> None:
        self.active = True
        self._on_show(**kwargs)

    def hide(self) -> None:
        self.active = False

    def is_active(self) -> bool:
        return self.active

    # hook for subclasses
    @abstractmethod
    def _on_show(self, **kwargs) -> None: ...

    def draw_overlay(self, surface: pygame.Surface) -> None:
        # draw a dim overlay; subclasses call this from their draw()
        overlay = surface.copy()
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

    def handle_event(self, event: pygame.event.Event):
        if not self.active:
            return False

        # ESC closes modal
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return True

        # Only mouse events matter for modal UI
        if event.type not in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ):
            return False

        # subclass handle its own components
        self._handle_components(event)

        # Panel-level buttons always use global coords
        if event.type == pygame.MOUSEMOTION:
            self.panel.apply_button.on_mouse_move(event.pos)
            self.panel.cancel_button.on_mouse_move(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.panel.apply_button.on_mouse_down(event.pos)
            self.panel.cancel_button.on_mouse_down(event.pos)

        return True

    @abstractmethod
    def _handle_components(self, event):
        """Subclasses override this to handle sliders/columns/etc."""
        pass
