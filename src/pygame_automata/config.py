# src/pygame_automata/config.py

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT"))


@dataclass
class EngineConfig:
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    bit_size: int = 8
    cell_size: int = 3
    pause_sec: int = 2
    timestep_ms: int = 5
    show_rulebox: bool = False
    output_dir: Path = Path.joinpath(PROJECT_ROOT, "examples")
    assets_dir: Path = Path.joinpath(PROJECT_ROOT, "assets")
    in_order: bool = False
