# src/pygame_automata/config.py

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT"))


@dataclass
class Config:
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    bit_size: int = 8
    cell_size: int = 3
    post_sim_pause_ms: int = 1000
    output_dir: Path = Path.joinpath(PROJECT_ROOT, "examples")
    assets_dir: Path = Path.joinpath(PROJECT_ROOT, "assets")
