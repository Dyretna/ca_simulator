from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..ca_simulator import CASimulator


ColorTuple = Tuple[int, int, int, int]


class Actions:
    def __init__(self, runner: "CASimulator"):
        self.runner = runner
        self.config = runner.config

    # --- Setters ---
    def set_resolution(self, w, h):
        self.runner.display_changes = True
        self.config.display.width = w
        self.config.display.height = h

    def set_fullscreen(self, fs):
        self.runner.display_changes = True
        self.config.display.fullscreen = fs

    def set_ruleset(self, b):
        self.config.engine.bit_size = b

    def set_cellsize(self, cs):
        self.config.engine.cell_size = cs

    def set_random_mode(self, m):
        self.config.engine.random_gen = m

    def set_autorun(self, ar):
        self.config.general.auto_run = ar

    def set_info(self, inf):
        self.config.general.show_info = inf

    # --- Toggles ---
    def toggle_save(self) -> None:
        "Save when CA simulation is done"
        self.runner.save_flag = not self.runner.save_flag

    def toggle_autorun(self) -> None:
        self.config.general.auto_run = not self.config.general.auto_run

    def toggle_fullscreen(self) -> None:
        self.runner.toggle_fullscreen()

    def toggle_info(self) -> None:
        """Toggle information overlay."""
        self.config.general.show_info = not self.config.general.show_info

    def toggle_random_mode(self) -> None:
        self.config.engine.random_gen = not self.config.engine.random_gen
        self.update_settings()

    def set_fg_color(self, c: ColorTuple) -> None:
        self.config.colors.ca_fg_color = (c[0], c[1], c[2], c[3])
        self.update_settings()

    def set_bg_color(self, c: ColorTuple) -> None:
        self.config.colors.ca_bg_color = (c[0], c[1], c[2], c[3])
        self.update_settings()

    # --- play and stop ---

    def play(self):
        """Plays next or resets the simulation"""
        self.runner.play()

    def quit(self) -> None:
        """Stop the main loop, and quits pygame."""
        self.runner.quit()

    # --- Settings ---

    def update_settings(self):
        self.runner.update_settings()
        print("Display or Engine Updated")

    def settings_is_active(self):
        return self.runner.settings_is_active()

    def open_settings(self) -> None:
        """Show the settings screen as a modal view."""
        self.runner.open_settings()
