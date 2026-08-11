import random

from .rules import RulesetBase, get_ruleset


class CAEngine:
    def __init__(
        self,
        bit_size: int,
        ruleset_code: int,
        width: int,
        cell_size: int,
        random: bool,
    ):
        self.bit_size: int = bit_size
        self.ruleset: RulesetBase = get_ruleset(bit_size)
        self.ruleset_code = ruleset_code
        self.random = random

        self.width = width
        self.cell_size = cell_size

        self.max_rule = (1 << self.ruleset.bit_size) - 1

        # runtime state
        self.generation = 0
        self.rules = self.ruleset.decode_ruleset(self.ruleset_code)
        self.cells = self.ruleset.make_initial_cells(self.width, self.cell_size)

    # --------------------------------------------------------------------

    def step(self):
        """Generate next generation of cells."""

        self.cells = self.ruleset.next_generation(self.cells, self.rules)
        self.generation += 1
        return self.cells

    def simulation_done(self, height: int) -> bool:
        """Check if we reached bottom of screen."""

        return (self.generation * self.cell_size) >= height

    def reset(self):
        """Reset simulation and pick next rule."""

        if self.random:
            self.ruleset_code = random.randint(0, self.max_rule)
        else:
            self.ruleset_code = (self.ruleset_code + 1) & self.max_rule

        self.rules = self.ruleset.decode_ruleset(self.ruleset_code)
        self.generation = 0
        self.cells = self.ruleset.make_initial_cells(self.width, self.cell_size)

        return self.ruleset_code
