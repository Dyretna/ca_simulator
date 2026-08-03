import random
import time
from pathlib import Path

import pygame

from ..config import Config
from .rules import RulesetBase


class CA1DRunner:
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

        # ruleset
        self.ruleset: RulesetBase = rulesetType()
        self.ruleset_code = ruleset_code
        self.in_order = in_order

        self.max_rule = (1 << self.ruleset.bit_len) - 1

        # runtime state
        self.generation = 0
        self.cells = None
        self.rules = None
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

        # initial rule + cells
        self.rules = self.ruleset.decode_ruleset(self.ruleset_code)
        self.cells = self.ruleset.make_initial_cells(self.width, self.cell_size)

        print(
            f"Current Rule: {self.ruleset_code} "
            f"({self.ruleset_code:0{self.ruleset.bit_len}b})"
        )

        self.screen.fill(self.bg_color)

        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        done = True
                    if event.key == pygame.K_s:
                        self.save_flag = True

            # draw
            self.draw_generation(self.screen, self.cells)
            if self.show_rulebox:
                self.draw_rulebox(self.screen, self.ruleset_code)

            # next generation
            self.cells = self.ruleset.next_generation(self.cells, self.rules)

            # reset when full
            if (self.generation * self.cell_size) >= self.height:
                time.sleep(self.pause_sec)

                if self.save_flag:
                    self.save_flag = self.save(self.screen)

                self.reset_simulation()

            else:
                pygame.display.update(
                    (0, self.generation * self.cell_size, self.width, self.cell_size)
                )
                self.generation += 1

            clock.tick(1000 // self.timestep_ms)

        pygame.quit()

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------
    def reset_simulation(self):
        # next rule
        if self.in_order:
            self.ruleset_code = (self.ruleset_code + 1) & self.max_rule
        else:
            self.ruleset_code = random.randint(0, self.max_rule)

        self.rules = self.ruleset.decode_ruleset(self.ruleset_code)

        print(
            f"Current Rule: {self.ruleset_code} "
            f"({self.ruleset_code:0{self.ruleset.bit_len}b})"
        )

        # reset generation + cells
        self.generation = 0
        self.cells = self.ruleset.make_initial_cells(self.width, self.cell_size)

        # clear screen
        self.screen.fill(self.bg_color)
        pygame.display.flip()

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def draw_generation(self, screen, cells):
        y = self.generation * self.cell_size
        width = screen.get_width()

        for i, cell in enumerate(cells):
            x = i * self.cell_size
            if x >= width:
                break

            color = self.fill_color if cell == 1 else self.bg_color
            # debug
            # print("i, cell, color in draw generation: ", i, cell, color)

            pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size))

    def draw_rulebox(self, screen, rule_code):
        font = pygame.font.SysFont("consolas", 20)

        bit_str = f"{rule_code:0{self.ruleset.bit_len}b}"
        grouped = " ".join(bit_str[i : i + 8] for i in range(0, len(bit_str), 8))

        text_str = f"Rule: {rule_code} ({grouped})"
        text = font.render(text_str, True, (255, 255, 255))

        text_w, text_h = font.size(text_str)
        padding = 10
        box_w = text_w + padding * 2
        box_h = text_h + padding

        # create transperent surface
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 120))  # last value alpha (0-255)

        screen.blit(box, (0, 0))
        screen.blit(text, (padding, padding // 2))

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------
    def save(self, screen) -> bool:
        Path(self.save_folder).mkdir(parents=True, exist_ok=True)
        filename = Path(self.save_folder) / f"rule_{self.ruleset_code}.png"
        pygame.image.save(screen, filename)
        print(f"Saved {self.ruleset_code}")
        return False


# ---------------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------------
if __name__ == "__main__":
    from .rules import get_ruleset
    from .utils import text_to_rule

    config = Config(
        width=1920,
        height=1080,
        fullscreen=True,
        cell_size=5,
        pause_sec=2,
        timestep_ms=10,
        bg_color=(30, 20, 25),
        fill_color=(50, 50, 120),
        show_rulebox=True,
        save_folder="examples",
    )

    # --------------------------------
    # testing translating words to CA rules
    # --------------------------------

    text_str = "I <3 CA"
    ruleset_size = 64

    rulesetType = get_ruleset(ruleset_size)
    ruleset_code = text_to_rule(text_str, ruleset_size)

    print("text_str:", text_str)
    print("Rule:", ruleset_code)

    # ---------------------------------

    runner = CA1DRunner(
        config=config,
        rulesetType=rulesetType,
        ruleset_code=1,  # or test word_to_rule above
        in_order=False,
    )

    runner.run()
