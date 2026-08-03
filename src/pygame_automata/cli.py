"""
Command-line interface for pygame_automata.

Allows running the CA visualizer with configurable parameters:
- rule code
- text-to-rule conversion
- ruleset size
- fullscreen toggle
- window size
- colors
- in-order mode
"""

import argparse

from pygame_automata.config import Config
from pygame_automata.core.rules import get_ruleset
from pygame_automata.core.utils import text_to_rule
from pygame_automata.main import CA1dDrawer


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the 1D cellular automaton visualizer."
    )

    # --- rule selection ---
    parser.add_argument(
        "--rule",
        type=int,
        default=None,
        help="Numeric rule code (0-255 or custom ruleset size).",
    )

    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Convert text into a rule using text_to_rule().",
    )

    parser.add_argument(
        "--ruleset-size",
        type=int,
        default=64,
        help="Number of rules in the ruleset (default: 64).",
    )

    parser.add_argument(
        "--in-order",
        action="store_true",
        help="Cycle rules in order instead of random.",
    )

    # --- display ---
    parser.add_argument("--width", type=int, default=1920, help="Window width.")

    parser.add_argument("--height", type=int, default=1080, help="Window height.")

    parser.add_argument(
        "--fullscreen", action="store_true", help="Enable fullscreen mode."
    )

    parser.add_argument(
        "--cell-size", type=int, default=5, help="Pixel size of each cell."
    )

    # --- timing ---
    parser.add_argument(
        "--pause-sec",
        type=float,
        default=2.0,
        help="Pause duration between rule changes.",
    )

    parser.add_argument(
        "--timestep-ms", type=int, default=10, help="Delay between generations."
    )

    # --- colors ---
    parser.add_argument(
        "--bg-color", type=str, default="30,20,25", help="Background color as R,G,B."
    )

    parser.add_argument(
        "--fill-color", type=str, default="50,50,120", help="Fill color as R,G,B."
    )

    # --- saving ---
    parser.add_argument(
        "--save-folder",
        type=str,
        default="examples",
        help="Folder to save screenshots.",
    )

    return parser.parse_args()


def parse_color(s: str):
    """Convert 'R,G,B' into a tuple."""
    parts = s.split(",")
    return tuple(int(p) for p in parts)


def main():
    args = parse_args()

    # --- config ---
    config = Config(
        width=args.width,
        height=args.height,
        fullscreen=args.fullscreen,
        cell_size=args.cell_size,
        pause_sec=args.pause_sec,
        timestep_ms=args.timestep_ms,
        bg_color=parse_color(args.bg_color),
        fill_color=parse_color(args.fill_color),
        show_rulebox=True,
        save_folder=args.save_folder,
    )

    # --- ruleset ---
    rulesetType = get_ruleset(args.ruleset_size)

    if args.text:
        ruleset_code = text_to_rule(args.text, args.ruleset_size)
    elif args.rule is not None:
        ruleset_code = args.rule
    else:
        ruleset_code = 1  # default

    print("Rule:", ruleset_code)

    # --- runner ---
    runner = CA1dDrawer(
        config=config,
        rulesetType=rulesetType,
        ruleset_code=ruleset_code,
        in_order=args.in_order,
    )

    runner.run()


if __name__ == "__main__":
    main()
