
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
