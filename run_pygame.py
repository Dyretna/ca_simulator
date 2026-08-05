from pygame_automata.core.rules import get_ruleset
from pygame_automata.ui.pygame_runner import PygameRunner

rulesetType = get_ruleset(8)

runner = PygameRunner(
    rulesetType=rulesetType,
    ruleset_code=30,
    width=1920,
    height=1080,
    in_order=False,
)

runner.run()
