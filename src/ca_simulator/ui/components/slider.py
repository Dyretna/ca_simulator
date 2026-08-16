import pygame


class Slider:
    def __init__(self, min_val: int, max_val: int, length: int):
        self.min_val = min_val
        self.max_val = max_val
        self.length = length
        self.value = max_val // 2

        self.surf = pygame.Surface((length + 40, 40), pygame.SRCALPHA)
        self.rect = self.surf.get_rect()

        self.bar_rect = pygame.Rect(20, 16, length, 8)
        self.handle_rect = pygame.Rect(0, 0, 20, 20)

        self.dragging = False

        self._update_handle()

    # ------------------------------------------------------
    # public API
    # ------------------------------------------------------

    def draw(self, target: pygame.Surface) -> None:
        self.surf.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surf, (180, 180, 180), self.bar_rect, border_radius=4)
        pygame.draw.rect(self.surf, (255, 255, 255), self.handle_rect, border_radius=4)
        pygame.draw.rect(
            self.surf, (0, 0, 0), self.handle_rect, width=2, border_radius=4
        )
        target.blit(self.surf, self.rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type not in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ):
            return
        mx, my = event.pos

        # convert global -> local inside slider surface
        lx = mx - self.rect.x
        ly = my - self.rect.y

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(lx, ly) or self.bar_rect.collidepoint(
                lx, ly
            ):
                self.dragging = True
                self._set_value_from_local_x(lx)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_value_from_local_x(lx)

    # ------------------------------------------------------
    # private helpers
    # ------------------------------------------------------

    def _update_handle(self) -> None:
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.bar_rect.left + t * self.bar_rect.width
        self.handle_rect.centery = self.bar_rect.centery

    def _set_value_from_local_x(self, lx: int):
        x = max(self.bar_rect.left, min(lx, self.bar_rect.right))
        t = (x - self.bar_rect.left) / self.bar_rect.width
        self.value = int(self.min_val + t * (self.max_val - self.min_val))
        self._update_handle()
