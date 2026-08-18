from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from ..ca_simulator import CASimulator


ColorTuple = Tuple[int, int, int, int]


class Actions:
    """
    Actions is the interface layer between the UI and CASimulator.

    Only immediate UI-driven actions live here:
    - toggles (fullscreen, autorun, random mode, info overlay)
    - opening modal views (settings, colorpicker)
    - play/quit commands
    - update_settings() after Settings commits buffered config

    SettingsScreen no longer calls setters here; it writes to its own
    local_state buffer and commits via state_to_config().
    """

    def __init__(self, runner: "CASimulator"):
        self.runner = runner
        self.config = runner.config

    # ---------------------------------------------------------
    # General actions in use by UIBar
    # ---------------------------------------------------------

    @property
    def save_flag(self):
        return self.runner.save_flag

    def toggle_save(self) -> None:
        "Save when CA simulation is done"
        self.runner.save_flag = not self.runner.save_flag

    def toggle_autorun(self) -> None:
        self.config.general.auto_run = not self.config.general.auto_run

    def toggle_fullscreen(self) -> None:
        self.runner.toggle_fullscreen()

    def toggle_random_mode(self) -> None:
        self.config.engine.random_gen = not self.config.engine.random_gen
        self.update_settings()

    def play(self):
        """Plays next or resets the simulation"""
        self.runner.play()

    def quit(self) -> None:
        """Stop the main loop, and quits pygame."""
        self.runner.quit()

    # --- Settings ---

    def update_settings(self):
        self.runner.update_settings()
        print("Settings Updated")

    def settings_is_active(self) -> bool:
        return self.runner.settings_screen.is_active()

    def open_settings(self) -> None:
        """Show the settings screen as a modal view."""
        if not self.settings_is_active():
            self.runner.settings_screen.show()

    # --- Colorpicker ---

    def set_fg_color(self, c: ColorTuple) -> None:
        self.config.colors.ca_fg_color = (c[0], c[1], c[2], c[3])
        self.update_settings()

    def set_bg_color(self, c: ColorTuple) -> None:
        self.config.colors.ca_bg_color = (c[0], c[1], c[2], c[3])
        self.update_settings()

    def open_fg_picker(self):
        self.runner.colorpicker.show(
            input_color=self.config.colors.ca_fg_color,
            callback=self.set_fg_color,
        )

    def open_bg_picker(self):
        self.runner.colorpicker.show(
            input_color=self.config.colors.ca_bg_color,
            callback=self.set_bg_color,
        )

    # --- Information Overlay ---

    def toggle_info(self) -> None:
        """Toggle information overlay."""
        if self.runner.info_overlay.is_active():
            self.runner.info_overlay.hide()
        else:
            self.runner.info_overlay.show()

    def info_is_active(self) -> bool:
        return self.runner.info_overlay.is_active()
