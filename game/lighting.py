import pygame


class DarknessSystem:
    """Applies a smooth, player-centred visibility mask to gameplay."""

    DARKNESS_ALPHA = 220
    ENTITY_ALPHA = 115
    TRANSITION_SPEED = 4.0
    VISIBILITY_RADIUS = 135

    def __init__(
        self,
        size,
        visibility_radius=VISIBILITY_RADIUS,
        darkness_alpha=DARKNESS_ALPHA,
        entity_alpha=ENTITY_ALPHA,
    ):
        self.size = tuple(size)
        self.visibility_radius = visibility_radius
        self.darkness_alpha = darkness_alpha
        self.entity_alpha = entity_alpha
        self.intensity = 0.0
        self._overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self._entity_surface = pygame.Surface(self.size, pygame.SRCALPHA)

    def update(self, dt, light_value):
        target = 1.0 if self._is_dark(light_value) else 0.0
        step = self.TRANSITION_SPEED * max(0.0, dt)
        difference = target - self.intensity
        if abs(difference) <= step:
            self.intensity = target
        else:
            self.intensity += step if difference > 0 else -step

    def apply(
        self,
        screen,
        player_center,
        draw_entities=None,
        entity_offset=(0, 0),
    ):
        """Darken the scene and optionally redraw dim entities above the mask."""
        if self.intensity <= 0:
            return

        center = (round(player_center[0]), round(player_center[1]))
        alpha = round(self.darkness_alpha * self.intensity)
        self._overlay.fill((0, 0, 0, alpha))
        pygame.draw.circle(
            self._overlay,
            (0, 0, 0, 0),
            center,
            self.visibility_radius,
        )
        screen.blit(self._overlay, (0, 0))

        if draw_entities is None:
            return

        self._entity_surface.fill((0, 0, 0, 0))
        draw_entities(self._entity_surface)
        local_center = (
            center[0] - round(entity_offset[0]),
            center[1] - round(entity_offset[1]),
        )
        pygame.draw.circle(
            self._entity_surface,
            (0, 0, 0, 0),
            local_center,
            self.visibility_radius,
        )
        self._entity_surface.set_alpha(
            round(self.entity_alpha * self.intensity)
        )
        screen.blit(self._entity_surface, entity_offset)
        self._entity_surface.set_alpha(None)

    @staticmethod
    def _is_dark(light_value):
        try:
            return float(light_value) == 0.0
        except (TypeError, ValueError):
            return False
