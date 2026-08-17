import pygame

from ...config import Config
from ..theme import DEFAULT_FONT


class InformationOverlay:
    """Draws the information overlay on top of the CA surface."""

    def __init__(self, config: Config):
        self.config = config

    def draw(self, surface: pygame.Surface, ruleset_code: int) -> None:
        font = pygame.font.SysFont(**DEFAULT_FONT)

        # rule bits
        bit_str = f"{ruleset_code:0{self.config.engine.bit_size}b}"
        grouped = " ".join(bit_str[i : i + 8] for i in range(0, len(bit_str), 8))

        lines = [
            f"Rule: {ruleset_code} ({grouped})",
            f"Bit Size: {self.config.engine.bit_size}",
            f"Cell Size: {self.config.engine.cell_size}",
        ]

        padding = 10
        y = 0

        for line in lines:
            text_surf = font.render(line, True, (255, 255, 255))
            w, h = font.size(line)

            # box size for THIS line only
            box_w = w + padding * 2
            box_h = h + padding

            # background box
            box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box.fill((0, 0, 0, 120))
            surface.blit(box, (0, y))

            # text
            surface.blit(text_surf, (padding, y + padding // 2))

            # next line below
            y += box_h
