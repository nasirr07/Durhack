from dataclasses import dataclass
from enum import Enum
import math
import random

import pygame

from collision import check_collision


class HazardPhase(Enum):
    IDLE = "idle"
    WARNING = "warning"
    BOULDERS = "boulders"
    COOLDOWN = "cooldown"


class TiltDetector:
    def __init__(self, change_limit=4, window=2.0):
        self.change_limit = change_limit
        self.window = window
        self.last_direction = None
        self.change_times = []

    def sample(self, direction, timestamp):
        self._discard_expired(timestamp)
        direction = direction if direction in ("left", "right") else None
        if direction is None:
            return False

        if self.last_direction is not None and direction != self.last_direction:
            self.change_times.append(timestamp)
        self.last_direction = direction
        self._discard_expired(timestamp)

        if len(self.change_times) >= self.change_limit:
            self.reset()
            return True
        return False

    def reset(self):
        self.last_direction = None
        self.change_times.clear()

    def _discard_expired(self, timestamp):
        cutoff = timestamp - self.window
        self.change_times = [
            change_time
            for change_time in self.change_times
            if change_time > cutoff
        ]


@dataclass
class Boulder:
    x: float
    y: float
    size: int = 34
    speed: float = 430.0
    hit_player: bool = False

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.size, self.size)

    def update(self, dt):
        self.y += self.speed * dt


@dataclass
class WarningDebris:
    x: float
    y: float
    size: int
    speed: float

    def update(self, dt):
        self.y += self.speed * dt


class EarthquakeHazard:
    WARNING_DURATION = 1.5
    BOULDER_DURATION = 5.0
    COOLDOWN_DURATION = 9.0
    SPAWN_INTERVAL = 0.8
    MAX_BOULDERS = 3

    def __init__(self, screen_width, floor_y, seed=None):
        self.screen_width = screen_width
        self.floor_y = floor_y
        self.screen_height = floor_y
        self.random = random.Random(seed)
        self.detector = TiltDetector()
        self.phase = HazardPhase.IDLE
        self.phase_elapsed = 0.0
        self.clock = 0.0
        self.spawn_timer = 0.0
        self.debris = []
        self.boulders = []

    @property
    def shake_offset(self):
        if self.phase != HazardPhase.WARNING:
            return (0, 0)
        amplitude = 2
        return (
            round(math.sin(self.clock * 38.0) * amplitude),
            round(math.cos(self.clock * 31.0) * amplitude),
        )

    def update(self, dt, direction, player=None):
        dt = max(0.0, dt)
        self.clock += dt

        if self.phase == HazardPhase.IDLE:
            if self.detector.sample(direction, self.clock):
                self._start_warning()
            return

        self.phase_elapsed += dt

        if self.phase == HazardPhase.WARNING:
            self._update_debris(dt)
            if self.phase_elapsed >= self.WARNING_DURATION:
                self._start_boulders()
        elif self.phase == HazardPhase.BOULDERS:
            self._update_boulders(dt, player)
            if self.phase_elapsed >= self.BOULDER_DURATION:
                self._start_cooldown()
                return
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self._spawn_until_full(limit=len(self.boulders) + 1)
                self.spawn_timer = self.SPAWN_INTERVAL
        elif self.phase == HazardPhase.COOLDOWN:
            self._update_boulders(dt, player)
            if self.phase_elapsed >= self.COOLDOWN_DURATION:
                self.phase = HazardPhase.IDLE
                self.phase_elapsed = 0.0
                self.detector.reset()

    def draw(self, screen):
        if self.phase == HazardPhase.WARNING:
            for debris in self.debris:
                pygame.draw.rect(
                    screen,
                    (190, 185, 165),
                    pygame.Rect(
                        round(debris.x),
                        round(debris.y),
                        debris.size,
                        debris.size,
                    ),
                )
        elif self.phase in (HazardPhase.BOULDERS, HazardPhase.COOLDOWN):
            for boulder in self.boulders:
                pygame.draw.rect(screen, (95, 83, 75), boulder.rect)
                pygame.draw.rect(screen, (50, 45, 43), boulder.rect, 2)

    def _start_warning(self):
        self.phase = HazardPhase.WARNING
        self.phase_elapsed = 0.0
        self.debris = [
            WarningDebris(
                self.random.randrange(0, max(1, self.screen_width - 8)),
                self.random.randrange(-self.floor_y, 0),
                self.random.choice((3, 4, 5)),
                self.random.uniform(100.0, 190.0),
            )
            for _ in range(12)
        ]

    def _start_boulders(self):
        self.phase = HazardPhase.BOULDERS
        self.phase_elapsed = 0.0
        self.debris.clear()
        self.boulders.clear()
        self.spawn_timer = 0.0
        self._spawn_until_full(limit=1)

    def _start_cooldown(self):
        self.phase = HazardPhase.COOLDOWN
        self.phase_elapsed = 0.0
        self.debris.clear()

    def _update_debris(self, dt):
        for debris in self.debris:
            debris.update(dt)
        self.debris = [
            debris
            for debris in self.debris
            if debris.y < self.floor_y
        ]

    def _update_boulders(self, dt, player):
        remaining = []
        for boulder in self.boulders:
            boulder.update(dt)
            if boulder.rect.bottom >= self.floor_y or boulder.rect.top > self.floor_y:
                continue
            if (
                player is not None
                and not boulder.hit_player
                and check_collision(boulder.rect, player.rect)
            ):
                player.take_damage()
                boulder.hit_player = True
            remaining.append(boulder)
        self.boulders = remaining

    def _spawn_until_full(self, limit=None):
        target = self.MAX_BOULDERS if limit is None else min(limit, self.MAX_BOULDERS)
        while len(self.boulders) < target:
            size = self.random.choice((30, 34, 38))
            x = self.random.uniform(0, max(0, self.screen_width - size))
            self.boulders.append(Boulder(x, -size, size=size))
