from typing import Any, Dict, List, Tuple

import pygame

from pygame_automata.ui.button.text_button import TextButton
from pygame_automata.ui.theme import (
    SETTINGS_BG,
    SETTINGS_HIGHLIGHT,
    SETTINGS_PANEL_BG,
    SETTINGS_TEXT,
)


class SettingsScreen:
    """
    Modal settings overlay for adjusting resolution, ruleset size,
    cell size and rule generation mode.

    Design A:
    - Layout and rendering happen together in draw()
    - Click rects are created during rendering
    - Y-flow is linear and deterministic
    - No offsets, no sync problems
    """

    def __init__(self, runner) -> None:
        self.runner = runner
        self.active: bool = False

        # current values (copied from runner)
        self.width: int = runner.width
        self.height: int = runner.height
        self.cell_size: int = runner.cell_size
        self.in_order: bool = runner.engine.in_order
        self.bit_size: int = runner.engine.ruleset.bit_size

        # selectable options
        self.resolutions: List[Tuple[int, int]] = [(1280, 720), (1920, 1080)]
        self.ruleset_types: List[int] = [8, 16, 32, 64]
        self.cell_sizes: List[int] = list(range(1, 11))
        self.modes: List[str] = ["In Order", "Random"]

        # fonts
        self.font = pygame.font.SysFont("consolas", 20)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)

        # colors
        self.bg_color = SETTINGS_BG
        self.panel_color = SETTINGS_PANEL_BG
        self.text_color = SETTINGS_TEXT
        self.highlight_color = SETTINGS_HIGHLIGHT

        # layout storage (rebuilt every draw)
        self.rows: Dict[str, List[Tuple[pygame.Rect, Any]]] = {
            "resolution": [],
            "ruleset": [],
            "cellsize": [],
            "mode": [],
        }

        # buttons
        self.buttons: List[TextButton] = []
        self.apply_button: TextButton | None = None
        self.cancel_button: TextButton | None = None

        # panel geometry
        self.panel_x: int = 0
        self.panel_y: int = 0
        self.panel_w: int = 0
        self.panel_h: int = 0

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def show(self) -> None:
        """Activate settings screen and build buttons."""
        self.active = True
        self._build_buttons()

    def hide(self) -> None:
        """Deactivate settings screen."""
        self.active = False

    def is_active(self) -> bool:
        """Return True if settings overlay is visible."""
        return self.active

    # ------------------------------------------------------------
    # Button building
    # ------------------------------------------------------------
    def _build_buttons(self) -> None:
        """Compute panel geometry and create Apply/Cancel buttons."""
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

    # ------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle mouse and keyboard events for the settings screen."""
        if not self.active:
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.hide()
            return

        if event.type == pygame.MOUSEMOTION:
            for btn in self.buttons:
                btn.on_mouse_move(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                btn.on_mouse_down(event.pos)
            self._handle_click(event.pos)

    def _handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle clicks on option rows."""
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

    # ------------------------------------------------------------
    # Rendering + layout
    # ------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        """Render the settings panel and compute layout inline."""
        if not self.active:
            return

        w, h = surface.get_size()

        # dark overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # panel
        panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        panel.fill(self.panel_color)

        # title
        title = self.title_font.render("Settings", True, self.text_color)
        panel.blit(title, (20, 20))

        # reset rows
        self.rows = {"resolution": [], "ruleset": [], "cellsize": [], "mode": []}

        # linear y-flow
        y = 70

        # resolution
        y = self._draw_section_header(panel, "Resolution", y)
        y = self._draw_option_row(
            panel,
            y,
            [f"{rw} x {rh}" for (rw, rh) in self.resolutions],
            self._selected_resolution_index(),
            self.rows["resolution"],
            self.resolutions,
        )

        # ruleset
        y = self._draw_section_header(panel, "Ruleset bit length", y + 10)
        y = self._draw_option_row(
            panel,
            y,
            [str(b) for b in self.ruleset_types],
            self._selected_ruleset_index(),
            self.rows["ruleset"],
            self.ruleset_types,
        )

        # cell size
        y = self._draw_section_header(panel, "Cell size", y + 10)
        y = self._draw_option_row(
            panel,
            y,
            [str(cs) for cs in self.cell_sizes],
            self._selected_cellsize_index(),
            self.rows["cellsize"],
            self.cell_sizes,
        )

        # mode
        y = self._draw_section_header(panel, "Rule generation", y + 10)
        selected_mode = 0 if self.in_order else 1
        y = self._draw_option_row(
            panel,
            y,
            self.modes,
            selected_mode,
            self.rows["mode"],
            self.modes,
        )

        # blit panel
        surface.blit(panel, (self.panel_x, self.panel_y))

        # draw buttons
        for btn in self.buttons:
            btn.draw(surface)

    # ------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------
    def _draw_section_header(self, panel: pygame.Surface, text: str, y: int) -> int:
        """Draw a section header and return new y-position."""
        label = self.font.render(text, True, self.text_color)
        panel.blit(label, (20, y))
        return y + 25

    def _draw_option_row(
        self,
        panel: pygame.Surface,
        y: int,
        options: List[str],
        selected_index: int,
        store_list: List[Tuple[pygame.Rect, Any]],
        value_list: List[Any],
    ) -> int:
        """Draw one row of selectable options and store click rects."""
        x = 40
        spacing = 10

        for idx, label in enumerate(options):
            txt = self.font.render(label, True, self.text_color)
            rect = txt.get_rect(topleft=(x, y))

            box_rect = pygame.Rect(
                rect.x - 6,
                rect.y - 4,
                rect.width + 12,
                rect.height + 8,
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

    # ------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------
    def _selected_resolution_index(self) -> int:
        for i, (w, h) in enumerate(self.resolutions):
            if w == self.width and h == self.height:
                return i
        return 0

    def _selected_ruleset_index(self) -> int:
        for i, b in enumerate(self.ruleset_types):
            if b == self.bit_size:
                return i
        return 0

    def _selected_cellsize_index(self) -> int:
        for i, cs in enumerate(self.cell_sizes):
            if cs == self.cell_size:
                return i
        return 0

    # ------------------------------------------------------------
    # Apply changes
    # ------------------------------------------------------------
    def _apply_changes(self) -> None:
        """Apply selected settings to runner and rebuild engine."""
        self.runner.width = self.width
        self.runner.height = self.height
        self.runner.cell_size = self.cell_size
        self.runner.bit_size = self.bit_size
        self.runner.in_order = self.in_order

        self.runner.update_settings()
        self.hide()
