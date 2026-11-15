import math
import pygame


class DarknessSystem:
    """Applies a smooth darkness overlay scaled directly from the micro:bit light value (0..255)."""

    DARKNESS_ALPHA = 220
    ENTITY_ALPHA = 115
    TRANSITION_SPEED = 4.0
    VISIBILITY_RADIUS = 135
    MAX_LIGHT_VALUE = 255.0

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
        target = self._darkness_from_light(light_value)
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
        """Darken the scene based on the micro:bit light reading and keep a player visibility radius."""
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

    @classmethod
    def _darkness_from_light(cls, light_value):
        """Convert micro:bit light level (0=dark .. 255=bright) directly into darkness intensity (1.0 .. 0.0)."""
        try:
            value = float(light_value)
        except (TypeError, ValueError):
            return 0.0
        if not math.isfinite(value):
            return 0.0
        clamped = max(0.0, min(cls.MAX_LIGHT_VALUE, value))
        return (cls.MAX_LIGHT_VALUE - clamped) / cls.MAX_LIGHT_VALUE
