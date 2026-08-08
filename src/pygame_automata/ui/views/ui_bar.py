# src/pygame_automata/ui/pygame_ui/views/ui_bar.py

from typing import TYPE_CHECKING

import pygame

from pygame_automata.ui.button import ButtonBase, IconButton
from pygame_automata.ui.theme import UI_BAR_ALPHA, UI_BAR_BG

if TYPE_CHECKING:
    from pygame_automata.pygame_runner import PygameRunner


class UIBar:
    """
    Top-level UI bar view.

    This is a proper View in the UIState stack:
    - It draws itself
    - It handles its own mouse events
    - It owns its buttons
    - It calls runner actions (fullscreen, pause, save, settings, etc.)
    """

    def __init__(self, runner: "PygameRunner"):
        self.runner = runner

        # UI bar surface
        self.height = 60
        self.surface = pygame.Surface((runner.width, self.height), pygame.SRCALPHA)

        # style
        self.bg_color = UI_BAR_BG
        self.alpha = UI_BAR_ALPHA

        # buttons
        self.buttons: list[None | ButtonBase,] = []
        self._build_buttons()

        # internal state
        self.offset_y = 0

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface):
        # update offset
        self.offset_y = screen.get_height() - self.height

        # draw background
        self.surface.fill((*self.bg_color, self.alpha))
        screen.blit(self.surface, (0, self.offset_y))

        # draw buttons
        for btn in self.buttons:
            btn.draw(screen, self.offset_y)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self._on_mouse_move(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_mouse_down(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._on_mouse_up(event.pos)

    def _to_local(self, screen_pos):
        return screen_pos[0], screen_pos[1] - self.offset_y

    def _on_mouse_move(self, screen_pos):
        local = self._to_local(screen_pos)
        for btn in self.buttons:
            btn.on_mouse_move(local)

    def _on_mouse_down(self, screen_pos):
        local = self._to_local(screen_pos)
        for btn in self.buttons:
            btn.on_mouse_down(local)

    def _on_mouse_up(self, screen_pos):
        local = self._to_local(screen_pos)
        for btn in self.buttons:
            btn.on_mouse_up(local)

    # ------------------------------------------------------------------
    # Button construction
    # ------------------------------------------------------------------
    def _build_buttons(self):
        start = 10

        def add(icon: str, start: int, func, active=None):
            pos = (start, 10, 50, 40)
            icon_path = self.runner.assets_dir / icon
            self.buttons.append(IconButton(*pos, icon_path, func, active))

        # settings - bool
        add(
            "icon_settings.png",
            start,
            self.runner.open_settings,
            active=lambda: self.runner.settings_screen.is_active(),
        )

        # fullscreen - bool
        start += 60
        add(
            "icon_fullscreen.png",
            start,
            self.runner.toggle_fullscreen,
            active=lambda: self.runner.fullscreen,
        )

        # show rulebox - bool
        start += 60
        add(
            "icon_R.png",
            start,
            self.runner.toggle_rulebox,
            active=lambda: self.runner.show_rulebox,
        )

        # autorun - bool
        start += 60
        add(
            "icon_autorun.png",
            start,
            self.runner.toggle_autorun,
            active=lambda: self.runner.auto_run,
        )

        # save
        start += 120
        add("icon_save.png", start, self.runner.save)

        # play
        start += 60
        add("icon_play.png", start, self.runner.play)

        # stop (exit)
        start += 60
        add("icon_stop.png", self.runner.width - 60, self.runner.stop)
