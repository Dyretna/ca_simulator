# src/pygame_automata/ui/pygame_ui/button/icon_button.py

import pygame

from pygame_automata.ui.theme import BTN_ACTIVE_C, BTN_HOVER_C

from .base import ButtonBase


class IconButton(ButtonBase):
    def __init__(self, x, y, w, h, icon_path, callback, active=None):
        super().__init__(x, y, w, h, callback)

        self.active = active  # callable or None

        # circle geometry
        self.cx = x + w // 2
        self.cy = y + h // 2
        self.radius = min(w, h) // 2

        # load PNG
        img = pygame.image.load(icon_path).convert_alpha()

        # scale to circle diameter
        diameter = self.radius * 2
        self.icon_img = pygame.transform.smoothscale(img, (diameter, diameter))

    def on_mouse_move(self, local_pos):
        dx = local_pos[0] - self.cx
        dy = local_pos[1] - self.cy
        self.hover = dx * dx + dy * dy <= self.radius * self.radius

    def on_mouse_down(self, local_pos):
        dx = local_pos[0] - self.cx
        dy = local_pos[1] - self.cy
        if dx * dx + dy * dy <= self.radius * self.radius:
            self.callback()

    def draw(self, surface, offset_y):
        cy = self.cy + offset_y

        # listen if button is active
        is_active = self.active() if self.active else False

        if is_active:
            pygame.draw.circle(surface, BTN_ACTIVE_C, (self.cx, cy), self.radius)
        elif self.hover:
            pygame.draw.circle(surface, BTN_HOVER_C, (self.cx, cy), self.radius)

        img = self.icon_img
        x = self.cx - img.get_width() // 2
        y = cy - img.get_height() // 2
        surface.blit(img, (x, y))
