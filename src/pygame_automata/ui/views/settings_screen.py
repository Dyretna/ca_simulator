# src/pygame_automata/ui/pygame_ui/views/settings_screen.py

from typing import TYPE_CHECKING

import pygame

from pygame_automata.ui.theme import (
    DEFAULT_FONT,
    SETTINGS_PANEL_BG,
    SETTINGS_TITLE_C,
    TITLE_FONT,
)

from ..components import TextButton, TextButtonRow

if TYPE_CHECKING:
    from pygame_automata.pygame_runner import PygameRunner


class SettingsScreen:
    def __init__(self, runner: "PygameRunner"):
        self.config = runner.config
        self.actions = runner.actions
        self.active = False

        # fonts
        self.font = pygame.font.SysFont(**DEFAULT_FONT)
        self.title_font = pygame.font.SysFont(**TITLE_FONT)

        # rows
        self.rows = []

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def show(self):
        """Activate settings screen."""
        self.active = True
        self._build_panel()
        self._build_rows()
        self._build_apply_btn()
        self._build_cancel_btn()

    def hide(self):
        """Deactivate settings screen."""
        self.active = False

    def is_active(self):
        return self.active

    def handle_event(self, event: pygame.event.Event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return

        if event.type == pygame.MOUSEMOTION:
            # translate positions from global to local
            local_pos = (event.pos[0] - self.panel_x, event.pos[1] - self.panel_y)

            for row in self.rows:
                row.handle_mouse_move(local_pos)

            self.apply_button.on_mouse_move(event.pos)
            self.cancel_button.on_mouse_move(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # translate positions from global to local
            local_pos = (event.pos[0] - self.panel_x, event.pos[1] - self.panel_y)

            for row in self.rows:
                row.handle_mouse_down(local_pos)

            self.apply_button.on_mouse_down(event.pos)
            self.cancel_button.on_mouse_down(event.pos)

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        # dark overlay - dim background
        w, h = surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # clear panel
        self.settings_panel.fill(SETTINGS_PANEL_BG)

        # title
        title = self.title_font.render("Settings", True, SETTINGS_TITLE_C)
        self.settings_panel.blit(title, (20, 20))

        # Draw options row
        for row in self.rows:
            row.draw(self.settings_panel)

        # blit panel
        surface.blit(self.settings_panel, (self.panel_x, self.panel_y))

        # draw bottom buttons
        self.apply_button.draw(surface)
        self.cancel_button.draw(surface)

    # ------------------------------------------------------------
    # Build helpers
    # ------------------------------------------------------------
    def _build_panel(self):
        """Compute panel geometry."""
        w, h = pygame.display.get_window_size()
        self.panel_w = int(w * 0.6)
        self.panel_h = int(h * 0.6)
        self.panel_x = (w - self.panel_w) // 2
        self.panel_y = (h - self.panel_h) // 2

        self.settings_panel = pygame.Surface(
            (self.panel_w, self.panel_h), pygame.SRCALPHA
        )
        self.settings_panel.fill(SETTINGS_PANEL_BG)

    def _build_rows(self):
        """Create ButtonRow objects for each setting."""

        padding = 80
        row_size = 40

        res_row = TextButtonRow(padding, padding, "Resolution")
        for w, h in [(1280, 720), (1920, 1080)]:
            active = w == self.config.display.width and h == self.config.display.height
            res_row.add(
                f"{w}x{h}",
                lambda w=w, h=h: self.actions.set_resolution(w, h),
                active,
            )

        y = row_size
        fs_row = TextButtonRow(padding, padding + y, "Fullscreen")
        for fs in [True, False]:
            active = self.config.display.fullscreen == fs
            fs_row.add(
                "ON" if fs else "OFF",
                lambda fs=fs: self.actions.set_fullscreen(fs),
                active,
            )

        y += row_size
        rss_row = TextButtonRow(padding, padding + y, "Ruleset Size")
        for b in [8, 16, 32, 64]:
            active = self.config.engine.bit_size == b
            rss_row.add(str(b), lambda b=b: self.actions.set_ruleset(b), active)

        y += row_size
        cs_row = TextButtonRow(padding, padding + y, "Cell Size")
        for cs in list(range(1, 11)):
            active = self.config.engine.cell_size == cs
            cs_row.add(str(cs), lambda cs=cs: self.actions.set_cellsize(cs), active)

        y += row_size
        mode_row = TextButtonRow(padding, padding + y, "Random Mode")
        for mode in [True, False]:
            active = self.config.engine.random_gen == mode
            mode_row.add(
                "ON" if mode else "OFF",
                lambda mode=mode: self.actions.set_random_mode(mode),
                active,
            )

        y += row_size
        ar_row = TextButtonRow(padding, padding + y, "AutoRun")
        for ar in [True, False]:
            active = self.config.general.auto_run == ar
            ar_row.add(
                "ON" if ar else "OFF",
                lambda ar=ar: self.actions.set_autorun(ar),
                active,
            )

        y += row_size
        info_row = TextButtonRow(padding, padding + y, "Info Overlay")
        for inf in [True, False]:
            active = self.config.general.show_info == inf
            info_row.add(
                "ON" if inf else "OFF",
                lambda inf=inf: self.actions.set_info(inf),
                active,
            )

        self.rows = [res_row, fs_row, rss_row, cs_row, mode_row, ar_row, info_row]

    def _build_apply_btn(self):
        btn_y = self.panel_y + self.panel_h - 60

        self.apply_button = TextButton(
            self.panel_x + self.panel_w - 220,
            btn_y,
            100,
            40,
            "Apply",
            self.font,
            self._apply_changes,
        )

    def _build_cancel_btn(self):
        btn_y = self.panel_y + self.panel_h - 60
        self.cancel_button = TextButton(
            self.panel_x + self.panel_w - 110,
            btn_y,
            100,
            40,
            "Cancel",
            self.font,
            self.hide,
        )

    def _apply_changes(self):
        self.actions.update_settings()
        self.hide()
