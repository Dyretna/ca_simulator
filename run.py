# run_pygame

from pygame_automata.config import Config
from pygame_automata.pygame_runner import PygameRunner

config = Config()
runner = PygameRunner(config)

runner.run()
