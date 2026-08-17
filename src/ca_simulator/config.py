# src/pygame_automata/config.py

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DisplaySettings:
    width: int = 1920
    height: int = 1080
    fullscreen: bool = True


@dataclass
class GeneralSettings:
    auto_run: bool = False
    idle_pause_ms: int = 1000


@dataclass
class EngineSettings:
    bit_size: int = 8
    cell_size: int = 3
    random_gen: bool = True


@dataclass
class ColorSettings:
    ca_bg_color: tuple[int, int, int, int] = (10, 20, 30, 255)
    ca_fg_color: tuple[int, int, int, int] = (100, 130, 50, 255)


@dataclass
class PathsSettings:
    project_root: Path = Path.cwd()
    output_dir: Path = field(init=False)
    assets_dir: Path = field(init=False)

    def __post_init__(self):
        self.output_dir = self.project_root / "examples"
        self.assets_dir = self.project_root / "assets"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)


@dataclass
class Config:
    display: DisplaySettings = field(default_factory=DisplaySettings)
    general: GeneralSettings = field(default_factory=GeneralSettings)
    engine: EngineSettings = field(default_factory=EngineSettings)
    colors: ColorSettings = field(default_factory=ColorSettings)
    paths: PathsSettings = field(default_factory=PathsSettings)
