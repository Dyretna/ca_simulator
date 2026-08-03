import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT"))


@dataclass
class Config:
    width: int = 1920
    height: int = 1080
    fullscreen: bool = False
    cell_size: int = 5
    pause_sec: int = 2
    timestep_ms: int = 5
    bg_color: tuple[int, int, int] = (0, 0, 0)
    fill_color: tuple[int, int, int] = (20, 50, 100)
    show_rulebox: bool = False
    save_folder: Path = Path.joinpath(PROJECT_ROOT, "examples")
