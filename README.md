![Generated sample](examples/8bit_rule30.png)

# Elementary Cellular Automaton visualizer using pygame.

This project implements a scrolling 1D cellular automaton where each generation is drawn as a horizontal row of pixels. The automaton evolves
according to a Wolfram-style 3-cell neighbourhood rule (0-255), and the simulation resets with a new random ruleset once the screen is filled.

The project builds on David Colson's original example:
```
https://github.com/DavidColson/CellularAutomata
```

The engine and application architecture have been rewritten in an modular OOP-style to support multiple rulesets, dynamic configuration, and a full Pygame-based UI.


## Installation

### 1. Clone the repository

```bash
git clone git@github.com:Dyretna/ca_simulator.git
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
This project uses python-dotenv to get easy access to paths.  To make use of it, create a .env file and add path to project root folder:

```
PROJECT_ROOT=/home/User/Dokument/<path to project...>/ca_simulator
```

## Usage
Run the pygame visualizer:

```bash
python run.py
```

- The runner opens a pygame window and starts the automaton immediately.

- The toolbar at the bottom provides controls for autorun, play, fullscreen, random-mode, info-overlay, save, and settings.

- The settings panel allows further options that requires an updated display and engine.


## Current Project Structure
```
.
├── examples
│   ├── 8bit_rule30.png
│   ...
│
├── assets
│   ├── icon_fullscreen.png
│   ...
|
├── src
│   └── ca_simulator
│       ├── core
│       │   ├── utils.py
│       │   ├── __init__.py
│       │   ├── ca_engine.py
│       │   └── rules.py
│       ├── ui
│       │   ├── views
│       │   │   ├── ca_screen.py
│       │   │   ├── __init__.py
│       │   │   ├── settings_screen.py
│       │   │   └── ui_bar.py
│       │   ├── button
│       │   │   ├── base.py
│       │   │   ├── icon_button.py
│       │   │   ├── __init__.py
│       │   │   └── text_button.py
│       │   ├── theme.py
│       │   ├── controller.py
│       │   └── __init__.py
│       ├── pygame_runner.py
│       └── config.py
├── LICENSE
├── README.md
├── run.py
├── pyproject.toml
└── requirements.txt
```
