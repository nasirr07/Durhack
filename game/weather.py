from dataclasses import dataclass
import math
import random

import pygame


@dataclass
class Cloud:
    sprite: pygame.Surface
    x: float
    y: float
    speed: float

    @property
    def width(self):
        return self.sprite.get_width()

    def update(self, dt, screen_width):
        self.x -= self.speed * dt
        if self.x + self.width < 0:
            self.x = screen_width


class WeatherSystem:
    HOT_THRESHOLD = 25.0
    TRANSITION_SPEED = 1.5

    def __init__(self, width, height, sun=None, seed=None):
        self.width = width
        self.height = height
        self.random = random.Random(seed)
        self.hot_target = 0.0
        self.hot_intensity = 0.0
        self.clouds = self._create_clouds()
        self.sun = self._prepare_sun(sun)

    def update(self, dt, temperature):
        dt = max(0.0, dt)
        self.hot_target = 1.0 if self._is_hot(temperature) else 0.0
        difference = self.hot_target - self.hot_intensity
        step = self.TRANSITION_SPEED * dt
        if abs(difference) <= step:
            self.hot_intensity = self.hot_target
        else:
            self.hot_intensity += step if difference > 0 else -step

        for cloud in self.clouds:
            cloud.update(dt, self.width)

    def draw(self, screen):
        cloud_alpha = round(255 * (1.0 - self.hot_intensity))
        if cloud_alpha:
            for cloud in self.clouds:
                cloud.sprite.set_alpha(cloud_alpha)
                screen.blit(cloud.sprite, (round(cloud.x), round(cloud.y)))

        if self.sun is not None and self.hot_intensity:
            self.sun.set_alpha(round(255 * self.hot_intensity))
            screen.blit(
                self.sun,
                (
                    self.width - self.sun.get_width() - max(24, self.width // 24),
                    max(24, self.height // 18),
                ),
            )

    def _create_clouds(self):
        layout = (
            (0.04, 0.06, 0.15, 18.0),
            (0.40, 0.04, 0.12, 12.0),
            (0.72, 0.10, 0.14, 15.0),
            (0.20, 0.20, 0.10, 10.0),
            (0.58, 0.22, 0.17, 20.0),
            (0.82, 0.29, 0.08, 9.0),
        )
        clouds = []
        for index, (x_ratio, y_ratio, width_ratio, speed) in enumerate(layout):
            source = self._make_cloud_sprite(index)
            cloud_width = max(24, round(self.width * width_ratio))
            cloud_height = max(
                16,
                round(cloud_width * source.get_height() / source.get_width()),
            )
            sprite = pygame.transform.scale(source, (cloud_width, cloud_height))
            clouds.append(
                Cloud(
                    sprite,
                    self.width * x_ratio
                    + self.random.uniform(-0.02, 0.02) * self.width,
                    self.height * y_ratio
                    + self.random.uniform(-0.015, 0.015) * self.height,
                    speed * self.random.uniform(0.9, 1.1),
                )
            )
        return clouds

    @staticmethod
    def _make_cloud_sprite(variant):
        palette = (
            (232, 238, 238, 255),
            (245, 248, 244, 255),
            (220, 232, 233, 255),
        )
        shadow = (170, 197, 200, 255)
        surface = pygame.Surface((32, 18), pygame.SRCALPHA)
        body = palette[variant % len(palette)]
        blocks = (
            (2, 8, 28, 8),
            (7, 5, 16, 8),
            (12, 2, 10, 8),
        )
        if variant % 2:
            blocks = (
                (1, 9, 30, 7),
                (5, 5, 13, 8),
                (18, 7, 10, 7),
            )
        for rect in blocks:
            pygame.draw.rect(surface, shadow, rect)
        for rect in blocks[1:]:
            pygame.draw.rect(
                surface,
                body,
                (rect[0], rect[1], rect[2], max(3, rect[3] - 2)),
            )
        pygame.draw.rect(surface, body, (blocks[0][0] + 3, blocks[0][1], blocks[0][2] - 6, 5))
        pygame.draw.rect(surface, (255, 255, 248, 255), (blocks[-1][0] + 2, blocks[-1][1], 5, 3))
        return surface

    def _prepare_sun(self, sun):
        if sun is None:
            return None
        sun_size = max(32, round(min(self.width, self.height) * 0.26))
        prepared = pygame.transform.scale(sun, (sun_size, sun_size))
        prepared.set_alpha(0)
        return prepared

    @staticmethod
    def _is_hot(temperature):
        try:
            value = float(temperature)
        except (TypeError, ValueError):
            return False
        return math.isfinite(value) and value > WeatherSystem.HOT_THRESHOLD
