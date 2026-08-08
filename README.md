![Generated sample](examples/8bit_rule30.png)

# Elementary Cellular Automaton visualizer using pygame.

This module implements a scrolling 1D cellular automaton where each
generation is drawn as a horizontal row of pixels. The automaton evolves
according to a Wolfram-style 3-cell neighbourhood rule (0-255), and the
simulation resets with a new random ruleset once the screen is filled.

The code is an updated OOP version of David Colson's original
example:

    https://github.com/DavidColson/CellularAutomata

The neighbour evaluation uses bit shifts to compute the rule index
efficiently, replacing the original string-based binary conversion.
Additional helpers separate initialization, rule decoding, generation
updates, and rendering to make the logic easier to read and extend.

---

## Installation

### 1. Clone the repository

```bash
git clone git@github.com:Dyretna/pygame_automata.git
cd pygame_automata
```

### 2. Install in editable mode
Editable mode makes the package importable while you develop:

```bash
pip install -e .
```

This uses the pyproject.toml configuration and installs the package
located under src/pygame_automata.

### 3. Set path in .env
This project uses python-dotenv to get easy access to paths, for example
when saving visualisations. To make use of it, create a .env file and add
path to project root folder:

```
PROJECT_ROOT=/home/User/Dokument/<path to project...>/pygame_automata
```

## Usage
Run the pygame visualizer:

```bash
python run.py
```

or

```
python -m pygame_automata.ui.pygame_runner
```

The runner opens a pygame window and starts the automaton immediately.
The toolbar at the bottom provides controls for pause, play, fullscreen, save, and settings.

The settings panel allows changing:
- resolution
- cell size
- ruleset bit length
- rule generation mode (in‑order or random)


##  Features
- Multiple ruleset sizes (8, 16, 32, 64 bit)
- Pause and resume
- Save screenshot
- Fullscreen toggle
- Settings panel with resolution, cell size, and rule generation mode
- Random or sequential rule generation

## Planned additions
- Step forward / backward
- Color picker and random palettes
- Word‑to‑rule input
- Auto‑run toggle
- Multiple render modes

## Current Project Structure
Its currently in development (August 2026)

```
.
├── assets
│   ├── icon_fullscreen.png
│   ├── icon_pause.png
│   ├── icon_play.png
│   ├── icon_save.png
│   ├── icon_settings.png
│   └── icon_stop.png
├── examples
│   ├── 64bit_rule4981587084493143526.png
│   └── 8bit_rule30.png
├── src
│   └── pygame_automata
│       ├── core
│       │   ├── ca_engine.py
│       │   ├── __init__.py
│       │   ├── rules.py
│       │   └── utils.py
│       ├── ui
│       │   ├── button
│       │   │   ├── base.py
│       │   │   ├── icon_button.py
│       │   │   ├── __init__.py
│       │   │   └── text_button.py
│       │   ├── controller
│       │   │   ├── controller.py
│       │   │   └── ui_state.py
│       │   ├── views
│       │   │   ├── ca_screen.py
│       │   │   ├── __init__.py
│       │   │   ├── settings_screen.py
│       │   │   └── ui_bar.py
│       │   ├── __init__.py
│       │   └── theme.py
│       ├── config.py
│       └── pygame_runner.py
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
└── run.py
```
