# src/pygame_automata/ui/pygame_ui/button/base.py

from abc import ABC, abstractmethod

import pygame


class ButtonBase(ABC):
    """
    Base class for all buttons.

    Buttons are dumb:
    - they know their hover state
    - they can draw themselves
    - they can detect hover and clicks
    - they call a callback when clicked
    """

    def __init__(self, x: int, y: int, w: int, h: int, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback
        self.hover = False

    @abstractmethod
    def draw(self, surface: pygame.Surface, offset_y: int): ...

    @abstractmethod
    def on_mouse_move(self, local_pos: tuple[int, int]): ...

    @abstractmethod
    def on_mouse_down(self, local_pos: tuple[int, int]): ...

    def on_mouse_up(self, local_pos: tuple[int, int]):
        pass
