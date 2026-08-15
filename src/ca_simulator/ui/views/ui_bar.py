# src/pygame_automata/ui/pygame_ui/views/ui_bar.py

import pygame

from ...config import Config
from ..actions import Actions
from ..components import ButtonBase, ColorSwatchButton, IconButton
from ..theme import UI_BAR_ALPHA, UI_BAR_BG


class UIBar:
    def __init__(self, config: Config, actions: Actions):
        self.config = config
        self.actions = actions

        # UI bar surface
        self.width = self.config.display.width
        self.height = 60
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # style
        self.bg_color = UI_BAR_BG
        self.alpha = UI_BAR_ALPHA

        # buttons
        self.buttons: list[None | ButtonBase,] = []
        self._build_icon_buttons()
        self._build_cs_buttons()

        # internal state
        self.offset_y = 0

    # ------------------------------------------------------------------
    # Rebuild after display changes
    # ------------------------------------------------------------------
    def rebuild(self):
        self.width = self.config.display.width
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.buttons.clear()
        self._build_icon_buttons()
        self._build_cs_buttons()

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

        elif event.type == pygame.KEYDOWN:
            self._handle_key(event.key)

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

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self.actions.quit()
        elif key == pygame.K_SPACE:
            self.actions.play()
        elif key == pygame.K_a:
            self.actions.toggle_autorun()
        elif key == pygame.K_f:
            self.actions.toggle_fullscreen()
        elif key == pygame.K_i:
            self.actions.toggle_info()
        elif key == pygame.K_r:
            self.actions.toggle_random_mode()
        elif key == pygame.K_s:
            self.actions.toggle_save()

    # ------------------------------------------------------------------
    # Button construction
    # ------------------------------------------------------------------
    def _build_icon_buttons(self):
        start = 10

        def add(icon: str, start: int, func, active=None):
            pos = (start, 10, 50, 40)
            icon_path = self.config.paths.assets_dir / icon
            self.buttons.append(IconButton(*pos, icon_path, func, active))

        add(
            "icon_settings.png",
            start,
            self.actions.open_settings,
            active=lambda: self.actions.settings_is_active(),
        )

        start += 60
        add(
            "icon_fullscreen.png",
            start,
            self.actions.toggle_fullscreen,
            active=lambda: self.config.display.fullscreen,
        )

        start += 60
        add(
            "icon_i.png",
            start,
            self.actions.toggle_info,
            active=lambda: self.config.general.show_info,
        )

        start += 60
        add(
            "icon_R.png",
            start,
            self.actions.toggle_random_mode,
            active=lambda: self.config.engine.random_gen,
        )

        start += 60
        add(
            "icon_autorun.png",
            start,
            self.actions.toggle_autorun,
            active=lambda: self.config.general.auto_run,
        )

        start += 60
        add(
            "icon_save.png",
            start,
            self.actions.toggle_save,
            active=lambda: self.actions.save_flag,
        )

        start += 60
        add("icon_play.png", start, self.actions.play)

        # stop at the right end
        add("icon_standby.png", self.config.display.width - 60, self.actions.quit)

    def _build_cs_buttons(self):
        icon_path = self.config.paths.assets_dir / "icon_stop.png"

        start = 500
        pos = (start, 10, 50, 40)
        fg_btn = ColorSwatchButton(
            *pos,
            get_color=lambda: self.config.colors.ca_fg_color,
            icon_path=icon_path,
            callback=self.actions.open_fg_picker,
        )

        pos = (start + 60, 10, 50, 40)
        bg_btn = ColorSwatchButton(
            *pos,
            get_color=lambda: self.config.colors.ca_bg_color,
            icon_path=icon_path,
            callback=self.actions.open_bg_picker,
        )

        self.buttons.append(fg_btn)
        self.buttons.append(bg_btn)
