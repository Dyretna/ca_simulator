from pygame_automata.ui.pygame_runner import PygameRunner

runner = PygameRunner(
    bit_size=8,
    ruleset_code=30,
    width=1920,
    height=1080,
    in_order=False,
)

runner.run()
