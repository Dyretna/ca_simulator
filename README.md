![Generated sample](examples/8bit_rule30.png)

# Elementary Cellular Automaton visualizer using pygame.

This project implements a scrolling 1D cellular automaton where each generation is drawn as a horizontal row of pixels. The automaton evolves
according to a Wolfram-style 3-cell neighbourhood rule (0-255), and the simulation resets with a new random ruleset once the screen is filled.

The project builds on David Colson's original example:
```
https://github.com/DavidColson/CellularAutomata
```

The engine and application architecture have been rewritten in an modular OOP-style to support multiple rulesets, dynamic configuration, and a full Pygame-based UI.


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
│   └── ca_simulator
│       ├── core
│       │   ├── __init__.py
│       │   ├── ca_engine.py
│       │   ├── rules.py
│       │   └── utils.py
│       ├── ui
│       │   ├── components
│       │   │   ├── button
│       │   │   │   ├── __init__.py
│       │   │   │   ├── base.py
│       │   │   │   ├── color_swatch_button.py
│       │   │   │   ├── icon_button.py
│       │   │   │   └── text_button.py
│       │   │   ├── __init__.py
│       │   │   └── slider.py
│       │   ├── views
│       │   │   ├── __init__.py
│       │   │   ├── colorpicker.py
│       │   │   ├── settings_screen.py
│       │   │   └── ui_bar.py
│       │   ├── __init__.py
│       │   ├── actions.py
│       │   └── theme.py
│       ├──__init__.py
│       ├── ca_simulator.py
│       └── config.py
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
└── run.py

```
