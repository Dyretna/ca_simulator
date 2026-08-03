import time
from pathlib import Path

import pygame

from ..config import Config
from ..core.ca_engine import CAEngine
from ..core.rules import RulesetBase


class CLIRunner:
    def __init__(
        self,
        config: Config,
        rulesetType: RulesetBase,
        ruleset_code: int,
        in_order: bool,
    ):
        # store config constants
        self.width = config.width
        self.height = config.height
        self.fullscreen = config.fullscreen
        self.cell_size = config.cell_size
        self.pause_sec = config.pause_sec
        self.timestep_ms = config.timestep_ms
        self.bg_color = config.bg_color
        self.fill_color = config.fill_color
        self.show_rulebox = config.show_rulebox
        self.save_folder = config.save_folder

        # Engine
        self.engine = CAEngine(
            rulesetType=rulesetType,
            ruleset_code=ruleset_code,
            width=self.width,
            cell_size=self.cell_size,
            in_order=in_order,
        )

        self.screen = None
        self.save_flag = False

    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------
    def run(self):
        pygame.init()

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Cellular Automata Test")
        clock = pygame.time.Clock()

        if self.fullscreen:
            pygame.display.flip()
            pygame.display.toggle_fullscreen()

        print(f"Current Rule: {self.engine.ruleset_code}")

        self.screen.fill(self.bg_color)

        running = True

        while running:
            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_s:
                        self.save_flag = True

            # next generation
            cells = self.engine.step()

            # draw
            self.draw_generation(self.screen, cells)

            if self.show_rulebox:
                self.draw_rulebox(self.screen, self.engine.ruleset_code)

            # reset when full
            if self.engine.needs_reset(self.height):
                time.sleep(self.pause_sec)

                if self.save_flag:
                    self.save_flag = self.save(self.screen)

                new_rule = self.engine.reset()
                print(f"Current Rule: {new_rule}")

                self.screen.fill(self.bg_color)
                pygame.display.flip()

            else:
                pygame.display.update(
                    (
                        0,
                        self.engine.generation * self.cell_size,
                        self.width,
                        self.cell_size,
                    )
                )

            clock.tick(1000 // self.timestep_ms)

        pygame.quit()

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def draw_generation(self, screen, cells):
        y = self.engine.generation * self.cell_size
        width = screen.get_width()

        for i, cell in enumerate(cells):
            x = i * self.cell_size
            if x >= width:
                break

            color = self.fill_color if cell == 1 else self.bg_color
            pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size))

    def draw_rulebox(self, screen, rule_code):
        font = pygame.font.SysFont("consolas", 20)

        bit_str = f"{rule_code:0{self.engine.ruleset.bit_len}b}"
        grouped = " ".join(bit_str[i : i + 8] for i in range(0, len(bit_str), 8))

        text_str = f"Rule: {rule_code} ({grouped})"
        text = font.render(text_str, True, (255, 255, 255))

        text_w, text_h = font.size(text_str)
        padding = 10
        box_w = text_w + padding * 2
        box_h = text_h + padding

        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 120))

        screen.blit(box, (0, 0))
        screen.blit(text, (padding, padding // 2))

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------
    def save(self, screen) -> bool:
        Path(self.save_folder).mkdir(parents=True, exist_ok=True)
        filename = Path(self.save_folder) / f"rule_{self.engine.ruleset_code}.png"
        pygame.image.save(screen, filename)
        print(f"Saved {self.engine.ruleset_code}")
        return False
