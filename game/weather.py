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

@dataclass
class GroundFire:
    x: float
    height: float
    speed: float
    phase: float

    def update(self, dt):
        self.phase += self.speed * dt

    def draw(self, screen, ground_y):
        flicker = abs(math.sin(self.phase))

        flame_height = self.height * (0.6 + flicker * 0.4)

        # Outer flame
        pygame.draw.polygon(
            screen,
            (190, 35, 10),
            [
                (self.x - 12, ground_y),
                (self.x, ground_y - flame_height),
                (self.x + 12, ground_y),
            ]
        )

        # Inner flame
        pygame.draw.polygon(
            screen,
            (255, 100, 10),
            [
                (self.x - 7, ground_y),
                (self.x, ground_y - flame_height * 0.7),
                (self.x + 7, ground_y),
            ]
        )

        # Bright centre
        pygame.draw.polygon(
            screen,
            (255, 210, 50),
            [
                (self.x - 3, ground_y),
                (self.x, ground_y - flame_height * 0.35),
                (self.x + 3, ground_y),
            ]
        )


class WeatherSystem:
    HOT_THRESHOLD = 25.0
    TRANSITION_SPEED = 1.5

    WIND_MIN_INTERVAL = 10.0
    WIND_MAX_INTERVAL = 25.0

    WIND_MIN_DURATION = 2.0
    WIND_MAX_DURATION = 4.0

    WIND_STRENGTH = 350.0

    FIRE_THRESHOLD = 31.0
    FIRE_FADE_SPEED = 0.5

    @staticmethod
    def _is_fire_temperature(temperature):
        try:
            value = float(temperature)
        except (TypeError, ValueError):
            return False

        return math.isfinite(value) and value >= WeatherSystem.FIRE_THRESHOLD

    def __init__(self, width, height, sun=None, seed=None, wind_sound = None):
        self.width = width
        self.height = height
        self.random = random.Random(seed)
        self.hot_target = 0.0
        self.hot_intensity = 0.0
        self.clouds = self._create_clouds()
        self.sun = self._prepare_sun(sun)

        self.wind_sound = wind_sound
        self.wind_active = False
        self.wind_timer = 0.0
        self.wind_duration = 0.0
        self.wind_direction = 0
        self.wind_force = 0.0

        self.next_wind = self.random.uniform(
            self.WIND_MIN_INTERVAL,
            self.WIND_MAX_INTERVAL
        )

        self.ground_fires = []
        self.fire_intensity = 0.0

        for x in range(0, self.width, 30):
            self.ground_fires.append(
                GroundFire(
                    x=float(x),
                    height=self.random.randint(25, 65),
                    speed=self.random.uniform(3.0, 7.0),
                    phase=self.random.uniform(0, math.pi * 2)
                )
            )

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

        if self.wind_active:
            self.wind_timer += dt

            if self.wind_timer >= self.wind_duration:
                self.wind_active = False
                self.wind_force = 0.0

                self.next_wind = self.random.uniform(
                    self.WIND_MIN_INTERVAL,
                    self.WIND_MAX_INTERVAL
                )

        else:
            self.next_wind -= dt

            if self.next_wind <= 0:
                self.wind_active = True
                self.wind_timer = 0.0

                self.wind_duration = self.random.uniform(
                    self.WIND_MIN_DURATION,
                    self.WIND_MAX_DURATION
                )

                self.wind_direction = self.random.choice([-1, 1])

                self.wind_force = (
                    self.wind_direction * self.WIND_STRENGTH
                )

                if self.wind_sound is not None:
                    print("WIND GUST STARTED!")
                    self.wind_sound.play(fade_ms=1500)
        target_fire = (
            1.0
            if self._is_fire_temperature(temperature)
            else 0.0
        )

        if self.fire_intensity < target_fire:
            self.fire_intensity = min(
                target_fire,
                self.fire_intensity + self.FIRE_FADE_SPEED * dt
            )

        elif self.fire_intensity > target_fire:
            self.fire_intensity = max(
                target_fire,
                self.fire_intensity - self.FIRE_FADE_SPEED * dt
            )

        if self.fire_intensity > 0:
            for fire in self.ground_fires:
                fire.update(dt)

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

                # Draw ground fire
        if self.fire_intensity > 0:
            fire_surface = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            for fire in self.ground_fires:
                fire.draw(fire_surface, self.height)

            fire_surface.set_alpha(round(255 * self.fire_intensity))
            screen.blit(fire_surface, (0, 0))

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
