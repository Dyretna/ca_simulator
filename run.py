# run_pygame

from pygame_automata.config import EngineConfig
from pygame_automata.pygame_runner import PygameRunner

e_config = EngineConfig()
runner = PygameRunner(e_config)

runner.run()
