"""
Bit-shifted neighborhood decoding for Wolfram cellular automata.

Wolfram 1D cellular automata use a 3-cell neighborhood to determine the
next state of each cell. For every position i, the neighborhood consists of:

    left  = cells[i - 1]
    self  = cells[i]
    right = cells[i + 1]

Each neighborhood is a 3-bit pattern. For example:

    111, 110, 101, 100, 011, 010, 001, 000

Wolfram rules (0-255 for 8-bit rulesets) assign a next-state value to each
of these eight patterns. To look up the correct output efficiently, the
neighborhood is converted into an integer index by bit shifting:

    index = (left << 2) | (self << 1) | right

This packs the three bits into a number 0-7 without string operations.
The rule table is stored as a list or bitmask, so the next state is simply:

    next_cell = rules[index]

Bit shifting is used because it is fast, branch-free, and avoids the
overhead of building strings or tuples for every neighborhood. It also
generalizes cleanly to larger rulesets (16-bit, 32-bit, etc.) where the
same pattern (shift left, OR in the next bit) constructs the lookup index
for wider neighborhoods.
"""

from abc import ABC, abstractmethod
from typing import List


def get_ruleset(ruleset_size: int | str):
    rulesets = {
        8: Ruleset8bit(),
        16: Ruleset16bit(),
        32: Ruleset32bit(),
        64: Ruleset64bit(),
    }

    # normalize input
    if isinstance(ruleset_size, int):
        raw_int = ruleset_size
    elif isinstance(ruleset_size, str) and ruleset_size.isdigit():
        raw_int = int(ruleset_size)
    else:
        raise TypeError("Rule query must be an int or a numeric string.")

    # validate
    if raw_int not in rulesets:
        available = ", ".join(str(k) for k in rulesets.keys())
        raise ValueError(f"Available rulesets are {available} bit.")

    return rulesets[raw_int]


class RulesetBase(ABC):
    """Abstract base class for all neighbourhood-based rulesets."""

    @property
    @abstractmethod
    def bit_size(self) -> int:
        """Number of bits in the ruleset (8, 16, 32, ...)"""
        ...

    def decode_ruleset(self, code: int) -> List[int]:
        """Decode integer rule into reversed Wolfram bit order."""
        bits = list(f"{code:0{self.bit_size}b}")
        bits.reverse()
        return [int(b) for b in bits]

    def make_initial_cells(self, width: int, cell_size: int) -> List[int]:
        """Create initial cell row with a single active cell in the center."""
        count = width // cell_size
        cells = [0] * count
        cells[count // 2] = 1
        return cells

    @abstractmethod
    def apply_rule(self, *args, **kwargs) -> int:
        """Compute next cell state using neighbourhood index."""
        ...

    @abstractmethod
    def neighbourhood_index(self, cells: List[int], i: int) -> int:
        """Compute neighbourhood index for rendering."""
        ...

    @abstractmethod
    def next_generation(self, cells: List[int], ruleset: List[int]) -> List[int]:
        """Compute next generation of cells."""
        ...


# =====================================================================
# 8-bit ruleset (3-cell neighbourhood)
# =====================================================================


class Ruleset8bit(RulesetBase):
    @property
    def bit_size(self) -> int:
        return 8

    def apply_rule(self, left: int, middle: int, right: int, ruleset: List[int]) -> int:
        idx = (left << 2) | (middle << 1) | right
        return ruleset[idx]

    def neighbourhood_index(self, cells: List[int], i: int) -> int:
        length = len(cells)
        left = cells[(i - 1) % length]
        mid = cells[i]
        right = cells[(i + 1) % length]
        return (left << 2) | (mid << 1) | right

    def next_generation(self, cells: List[int], ruleset: List[int]) -> List[int]:
        new = []
        length = len(cells)
        for i in range(length):
            left = cells[(i - 1) % length]
            mid = cells[i]
            right = cells[(i + 1) % length]
            new.append(self.apply_rule(left, mid, right, ruleset))
        return new


# =====================================================================
# 16-bit ruleset (4-cell neighbourhood)
# =====================================================================


class Ruleset16bit(RulesetBase):
    @property
    def bit_size(self) -> int:
        return 16

    def apply_rule(self, a: int, b: int, c: int, d: int, ruleset: List[int]) -> int:
        idx = (a << 3) | (b << 2) | (c << 1) | d
        return ruleset[idx]

    def neighbourhood_index(self, cells: List[int], i: int) -> int:
        length = len(cells)
        a = cells[(i - 1) % length]
        b = cells[i]
        c = cells[(i + 1) % length]
        d = cells[(i + 2) % length]
        return (a << 3) | (b << 2) | (c << 1) | d

    def next_generation(self, cells: List[int], ruleset: List[int]) -> List[int]:
        new = []
        length = len(cells)
        for i in range(length):
            a = cells[(i - 1) % length]
            b = cells[i]
            c = cells[(i + 1) % length]
            d = cells[(i + 2) % length]
            new.append(self.apply_rule(a, b, c, d, ruleset))
        return new


# =====================================================================
# 32-bit ruleset (5-cell neighbourhood)
# =====================================================================


class Ruleset32bit(RulesetBase):
    @property
    def bit_size(self) -> int:
        return 32

    def apply_rule(
        self, a: int, b: int, c: int, d: int, e: int, ruleset: List[int]
    ) -> int:
        idx = (a << 4) | (b << 3) | (c << 2) | (d << 1) | e
        return ruleset[idx]

    def neighbourhood_index(self, cells: List[int], i: int) -> int:
        length = len(cells)
        a = cells[(i - 2) % length]
        b = cells[(i - 1) % length]
        c = cells[i]
        d = cells[(i + 1) % length]
        e = cells[(i + 2) % length]
        return (a << 4) | (b << 3) | (c << 2) | (d << 1) | e

    def next_generation(self, cells: List[int], ruleset: List[int]) -> List[int]:
        new = []
        length = len(cells)
        for i in range(length):
            a = cells[(i - 2) % length]
            b = cells[(i - 1) % length]
            c = cells[i]
            d = cells[(i + 1) % length]
            e = cells[(i + 2) % length]
            new.append(self.apply_rule(a, b, c, d, e, ruleset))
        return new


# =====================================================================
# 64-bit ruleset (6-cell neighbourhood)
# =====================================================================


class Ruleset64bit(RulesetBase):
    @property
    def bit_size(self) -> int:
        return 64

    def apply_rule(
        self, a: int, b: int, c: int, d: int, e: int, f: int, ruleset: List[int]
    ) -> int:
        idx = (a << 5) | (b << 4) | (c << 3) | (d << 2) | (e << 1) | f
        return ruleset[idx]

    def neighbourhood_index(self, cells: List[int], i: int) -> int:
        length = len(cells)
        a = cells[(i - 2) % length]
        b = cells[(i - 1) % length]
        c = cells[i]
        d = cells[(i + 1) % length]
        e = cells[(i + 2) % length]
        f = cells[(i + 3) % length]
        return (a << 5) | (b << 4) | (c << 3) | (d << 2) | (e << 1) | f

    def next_generation(self, cells: List[int], ruleset: List[int]) -> List[int]:
        new = []
        length = len(cells)
        for i in range(length):
            a = cells[(i - 2) % length]
            b = cells[(i - 1) % length]
            c = cells[i]
            d = cells[(i + 1) % length]
            e = cells[(i + 2) % length]
            f = cells[(i + 3) % length]
            new.append(self.apply_rule(a, b, c, d, e, f, ruleset))
        return new
