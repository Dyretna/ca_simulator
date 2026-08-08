import pygame

from pygame_automata.ui.button.text_button import TextButton
from pygame_automata.ui.theme import (
    SETTINGS_BG,
    SETTINGS_HIGHLIGHT,
    SETTINGS_PANEL_BG,
    SETTINGS_TEXT,
)


class SettingsScreen:
    def __init__(self, runner):
        self.runner = runner
        self.active = False

        self.width = runner.width
        self.height = runner.height
        self.cell_size = runner.cell_size
        self.in_order = runner.engine.in_order
        self.bit_size = runner.engine.ruleset.bit_size

        self.resolutions = [(1280, 720), (1920, 1080)]
        self.ruleset_types = [8, 16, 32, 64]
        self.cell_sizes = list(range(1, 11))
        self.modes = ["In Order", "Random"]

        self.font = pygame.font.SysFont("consolas", 20)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)

        self.bg_color = SETTINGS_BG
        self.panel_color = SETTINGS_PANEL_BG
        self.text_color = SETTINGS_TEXT
        self.highlight_color = SETTINGS_HIGHLIGHT

        self.rows = {"resolution": [], "ruleset": [], "cellsize": [], "mode": []}

        self.buttons = []
        self.apply_button = None
        self.cancel_button = None

        self.panel_x = 0
        self.panel_y = 0
        self.panel_w = 0
        self.panel_h = 0

    def show(self):
        self.active = True
        self._build_buttons()

    def hide(self):
        self.active = False

    def is_active(self):
        return self.active

    def _build_buttons(self):
        w, h = self.runner.screen.get_size()

        self.panel_w = int(w * 0.6)
        self.panel_h = int(h * 0.6)
        self.panel_x = (w - self.panel_w) // 2
        self.panel_y = (h - self.panel_h) // 2

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

        self.cancel_button = TextButton(
            self.panel_x + self.panel_w - 110,
            btn_y,
            100,
            40,
            "Cancel",
            self.font,
            self.hide,
        )

        self.buttons = [self.apply_button, self.cancel_button]

    def handle_event(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return

        if event.type == pygame.MOUSEMOTION:
            for btn in self.buttons:
                btn.on_mouse_move(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                btn.on_mouse_down(event.pos)
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        x, y = pos

        for rect, val in self.rows["resolution"]:
            if rect.collidepoint(x, y):
                self.width, self.height = val
                return

        for rect, val in self.rows["ruleset"]:
            if rect.collidepoint(x, y):
                self.bit_size = val
                return

        for rect, val in self.rows["cellsize"]:
            if rect.collidepoint(x, y):
                self.cell_size = val
                return

        for rect, val in self.rows["mode"]:
            if rect.collidepoint(x, y):
                self.in_order = val == "In Order"
                return

    def draw(self, surface):
        if not self.active:
            return

        w, h = surface.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        panel.fill(self.panel_color)

        title = self.title_font.render("Settings", True, self.text_color)
        panel.blit(title, (20, 20))

        y = 70

        y = self._draw_section_header(panel, "Resolution", y)
        self.rows["resolution"] = []
        y = self._draw_option_row(
            panel,
            y,
            [f"{rw} x {rh}" for (rw, rh) in self.resolutions],
            self._selected_resolution_index(),
            self.rows["resolution"],
            self.resolutions,
        )

        y = self._draw_section_header(panel, "Ruleset bit length", y + 10)
        self.rows["ruleset"] = []
        y = self._draw_option_row(
            panel,
            y,
            [str(b) for b in self.ruleset_types],
            self._selected_ruleset_index(),
            self.rows["ruleset"],
            self.ruleset_types,
        )

        y = self._draw_section_header(panel, "Cell size", y + 10)
        self.rows["cellsize"] = []
        y = self._draw_option_row(
            panel,
            y,
            [str(cs) for cs in self.cell_sizes],
            self._selected_cellsize_index(),
            self.rows["cellsize"],
            self.cell_sizes,
        )

        y = self._draw_section_header(panel, "Rule generation", y + 10)
        self.rows["mode"] = []
        selected_mode = 0 if self.in_order else 1
        y = self._draw_option_row(
            panel, y, self.modes, selected_mode, self.rows["mode"], self.modes
        )

        surface.blit(panel, (self.panel_x, self.panel_y))

        for btn in self.buttons:
            btn.draw(surface, offset_y=0)

    def _draw_section_header(self, panel, text, y):
        label = self.font.render(text, True, self.text_color)
        panel.blit(label, (20, y))
        return y + 25

    def _draw_option_row(
        self, panel, y, options, selected_index, store_list, value_list
    ):
        x = 40
        spacing = 10
        for idx, label in enumerate(options):
            txt = self.font.render(label, True, self.text_color)
            rect = txt.get_rect()
            rect.topleft = (x, y)

            box_rect = pygame.Rect(
                rect.x - 6, rect.y - 4, rect.width + 12, rect.height + 8
            )
            color = self.highlight_color if idx == selected_index else (40, 45, 60)
            pygame.draw.rect(panel, color, box_rect, border_radius=4)

            panel.blit(txt, rect.topleft)

            screen_rect = pygame.Rect(
                self.panel_x + box_rect.x,
                self.panel_y + box_rect.y,
                box_rect.width,
                box_rect.height,
            )

            store_list.append((screen_rect, value_list[idx]))
            x += box_rect.width + spacing

        return y + 40

    def _selected_resolution_index(self):
        for i, (w, h) in enumerate(self.resolutions):
            if w == self.width and h == self.height:
                return i
        return 0

    def _selected_ruleset_index(self):
        for i, b in enumerate(self.ruleset_types):
            if b == self.bit_size:
                return i
        return 0

    def _selected_cellsize_index(self):
        for i, cs in enumerate(self.cell_sizes):
            if cs == self.cell_size:
                return i
        return 0

    def _apply_changes(self):
        self.runner.width = self.width
        self.runner.height = self.height
        self.runner.cell_size = self.cell_size
        self.runner.bit_size = self.bit_size
        self.runner.in_order = self.in_order
        self.runner.update_settings()
        self.hide()
