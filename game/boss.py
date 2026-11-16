import math
import os
import random
import pygame

_CACHED_BOSS_DATA = {}
_CACHED_FIREBALL_SURFACE = None
_CACHED_HEAT_WAVE_SURFACE = None
_CACHED_INCANTATION_SURFACE = None
_CACHED_LASER_SURFACE = None

# Scale factor relative to the base 450x270 frame (1260x756 total frame, 350x495 visible boss body)
BOSS_SCALE = 2.8

FRAME_WIDTH = round(450 * BOSS_SCALE)                 # 1260
FRAME_HEIGHT = round(270 * BOSS_SCALE)                # 756
BODY_OFFSET_X_LEFT = round(166 * BOSS_SCALE)          # 465
BODY_OFFSET_Y = round(92 * BOSS_SCALE)                # 258
BODY_WIDTH = round(125 * BOSS_SCALE)                  # 350
BODY_HEIGHT = FRAME_HEIGHT - BODY_OFFSET_Y - 3        # 495
BODY_OFFSET_X_RIGHT = FRAME_WIDTH - BODY_OFFSET_X_LEFT - BODY_WIDTH

# Cleaver slash region in front of the boss during row_3 active frames (9..12)
ATTACK_OFFSET_X_LEFT = round(32 * BOSS_SCALE)         # 90
ATTACK_OFFSET_Y = round(97 * BOSS_SCALE)              # 272
ATTACK_WIDTH = BODY_OFFSET_X_LEFT - ATTACK_OFFSET_X_LEFT  # 375
ATTACK_HEIGHT = FRAME_HEIGHT - ATTACK_OFFSET_Y - 3    # 481
ATTACK_OFFSET_X_RIGHT = FRAME_WIDTH - ATTACK_OFFSET_X_LEFT - ATTACK_WIDTH
ACTIVE_ATTACK_FRAMES = (9, 10, 11, 12)

FIREBALL_TEMP_THRESHOLD = 26.0


def _is_over_fireball_temp(temperature):
    try:
        value = float(temperature)
    except (TypeError, ValueError):
        return False
    return math.isfinite(value) and value >= FIREBALL_TEMP_THRESHOLD


def load_fireball_surface():
    global _CACHED_FIREBALL_SURFACE
    if _CACHED_FIREBALL_SURFACE is not None:
        return _CACHED_FIREBALL_SURFACE

    fireball_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "assets", "boss", "fireball.png")
    )
    if os.path.exists(fireball_path):
        surf = pygame.image.load(fireball_path)
        if pygame.display.get_surface() is not None:
            surf = surf.convert_alpha()
    else:
        surf = pygame.Surface((64, 40), pygame.SRCALPHA)
        grid = [
            "........RRRRRR..................",
            ".....RRRRROOOORRRR..............",
            "...RRROOOOOYYYYOOORRRRR.........",
            "..RROOOOYYYYWWWWYYOOOOORRRRRR...",
            ".RROOOYYYWWWWWWWWYYYOOOOORRRRRR.",
            "RROOOYYWWWWWWWWWWWWYYOOOOOORRRRR",
            "RROOYYWWWWWWWWWWWWWWYYOOOOORRRR.",
            "RROOYYWWWWWWWWWWWWWWYYOOOOORRRR.",
            "RROOOYYWWWWWWWWWWWWYYOOOOOORRRRR",
            ".RROOOYYYWWWWWWWWYYYOOOOORRRRRR.",
            "..RROOOOYYYYWWWWYYOOOOORRRRRR...",
            "...RRROOOOOYYYYOOORRRRR.........",
            ".....RRRRROOOORRRR..............",
            "........RRRRRR..................",
        ]
        cmap = {
            "R": (210, 45, 20, 255),
            "O": (255, 130, 20, 255),
            "Y": (255, 220, 50, 255),
            "W": (255, 255, 230, 255),
        }
        for y, row in enumerate(grid):
            for x, ch in enumerate(row):
                if ch in cmap:
                    pygame.draw.rect(surf, cmap[ch], (x * 2, y * 2 + 6, 2, 2))

    _CACHED_FIREBALL_SURFACE = surf
    return surf


def load_heat_wave_surface():
    global _CACHED_HEAT_WAVE_SURFACE
    if _CACHED_HEAT_WAVE_SURFACE is not None:
        return _CACHED_HEAT_WAVE_SURFACE

    hw_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "assets", "boss", "heat_wave.png")
    )
    if os.path.exists(hw_path):
        surf = pygame.image.load(hw_path)
        if pygame.display.get_surface() is not None:
            surf = surf.convert_alpha()
    else:
        w, h = 64, 96
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for x in range(0, w, 4):
            top_edge = int(12 + 8 * math.sin(x * 0.45))
            bot_edge = h - int(8 + 6 * math.cos(x * 0.65))
            for y in range(0, h, 4):
                if top_edge <= y <= bot_edge:
                    colour = (
                        (200, 35, 15, 220)
                        if y < 24
                        else (245, 110, 20, 240)
                        if y < 56
                        else (255, 200, 40, 255)
                        if y < 78
                        else (255, 250, 210, 255)
                    )
                    pygame.draw.rect(surf, colour, (x, y, 4, 4))

    _CACHED_HEAT_WAVE_SURFACE = surf
    return surf


def load_incantation_surface():
    global _CACHED_INCANTATION_SURFACE
    if _CACHED_INCANTATION_SURFACE is not None:
        return _CACHED_INCANTATION_SURFACE

    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "assets", "boss", "incantation_circle.png")
    )
    if os.path.exists(path):
        surf = pygame.image.load(path)
        if pygame.display.get_surface() is not None:
            surf = surf.convert_alpha()
    else:
        low = pygame.Surface((36, 36), pygame.SRCALPHA)
        cx, cy = 17.5, 17.5
        for y in range(36):
            for x in range(36):
                d = math.hypot(x - cx, y - cy)
                if 15.2 <= d <= 17.2:
                    low.set_at((x, y), (205, 65, 10, 240))
                elif 11.2 <= d <= 12.8:
                    low.set_at((x, y), (255, 140, 20, 250))
                elif 4.2 <= d <= 5.8:
                    low.set_at((x, y), (255, 205, 55, 255))
                elif d <= 2.2:
                    low.set_at((x, y), (255, 245, 200, 255))
        surf = pygame.transform.scale(low, (144, 144))

    _CACHED_INCANTATION_SURFACE = surf
    return surf


def load_laser_surface():
    global _CACHED_LASER_SURFACE
    if _CACHED_LASER_SURFACE is not None:
        return _CACHED_LASER_SURFACE

    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "assets", "boss", "laser_beam.png")
    )
    if os.path.exists(path):
        surf = pygame.image.load(path)
        if pygame.display.get_surface() is not None:
            surf = surf.convert_alpha()
    else:
        bl = pygame.Surface((16, 11), pygame.SRCALPHA)
        for y in range(11):
            for x in range(16):
                if y in (1, 9) and x % 2 == 0:
                    bl.set_at((x, y), (205, 65, 10, 210))
                elif y in (2, 8):
                    bl.set_at((x, y), (235, 95, 15, 235))
                elif y in (3, 7):
                    bl.set_at((x, y), (255, 150, 25, 250))
                elif y in (4, 6):
                    bl.set_at((x, y), (255, 205, 60, 255))
                elif y == 5:
                    bl.set_at((x, y), (255, 248, 215, 255))
        surf = pygame.transform.scale(bl, (64, 44))

    _CACHED_LASER_SURFACE = surf
    return surf


class LaserIncantation:
    """Spawns a spinning orange pixel-art incantation circle that fires a straight laser beam at height y."""

    def __init__(
        self,
        origin_x,
        y,
        facing=-1,
        incantation_duration=1.8,
        beam_duration=0.65,
        beam_height=44,
        arena_width=2400,
        damage=1,
    ):
        self.origin_x = float(origin_x)
        self.y = float(y)
        self.facing = facing
        self.incantation_duration = float(incantation_duration)
        self.beam_duration = float(beam_duration)
        self.beam_height = int(beam_height)
        self.arena_width = int(arena_width)
        self.damage = damage
        self.age = 0.0
        self.active = True
        self.has_damaged_player = False

        self.circle_base = load_incantation_surface()
        # Keep a 36x36 low-res pixel-art copy so rotation stays chunky pixel art when scaled up
        self.circle_lowres = pygame.transform.scale(self.circle_base, (36, 36))
        self.circle_target_size = 152

        beam_tile = load_laser_surface()
        if beam_tile.get_height() != self.beam_height:
            beam_tile = pygame.transform.scale(
                beam_tile, (beam_tile.get_width(), self.beam_height)
            )

        if self.facing == -1:
            self.beam_x = 0
            self.beam_width = max(1, round(self.origin_x))
        else:
            self.beam_x = round(self.origin_x)
            self.beam_width = max(1, self.arena_width - self.beam_x)

        self.beam_surface = pygame.Surface(
            (self.beam_width, self.beam_height), pygame.SRCALPHA
        )
        tile_w = beam_tile.get_width()
        for tx in range(0, self.beam_width, tile_w):
            self.beam_surface.blit(beam_tile, (tx, 0))
        self.beam_mask = pygame.mask.from_surface(self.beam_surface)

    @property
    def firing(self):
        return (
            self.active
            and self.incantation_duration
            <= self.age
            < (self.incantation_duration + self.beam_duration)
        )

    @property
    def beam_rect(self):
        if not self.firing:
            return None
        return pygame.Rect(
            self.beam_x,
            round(self.y - self.beam_height / 2),
            self.beam_width,
            self.beam_height,
        )

    def update(self, dt):
        if not self.active:
            return
        self.age += dt
        if self.age >= self.incantation_duration + self.beam_duration:
            self.active = False

    def check_hit(self, player):
        if not self.firing or self.has_damaged_player:
            return False

        b_rect = self.beam_rect
        if b_rect is None or not b_rect.colliderect(player.rect):
            return False

        p_mask = getattr(player, "body_mask", None)
        if p_mask is None:
            p_mask = pygame.mask.Mask(player.rect.size, fill=True)

        offset = (player.rect.x - b_rect.x, player.rect.y - b_rect.y)
        if self.beam_mask.overlap(p_mask, offset) is not None:
            self.has_damaged_player = True
            return True
        return False

    def draw(self, screen):
        if not self.active:
            return

        # 1. Draw full laser beam once incantation completes (no preview line during charge-up)
        if self.firing:
            beam_age = self.age - self.incantation_duration
            remain_ratio = 1.0 - (beam_age / max(0.01, self.beam_duration))
            beam_copy = self.beam_surface.copy()
            beam_copy.set_alpha(min(255, max(0, round(255 * min(1.0, remain_ratio * 2.5)))))
            screen.blit(beam_copy, self.beam_rect)

        # 2. Draw rotating, fading-in orange pixel-art incantation circle at origin (rotated at low-res then scaled 4x)
        inc_progress = min(1.0, max(0.0, self.age / max(0.01, self.incantation_duration * 0.6)))
        scale = 0.35 + 0.65 * inc_progress
        # Step rotation angle to 15-degree increments for authentic pixel-art animation feel
        stepped_angle = round((self.age * 150.0) / 15.0) * 15.0
        rotated_low = pygame.transform.rotate(self.circle_lowres, stepped_angle)
        pixel_scale = (self.circle_target_size / 36.0) * scale
        scaled_w = max(8, round(rotated_low.get_width() * pixel_scale))
        scaled_h = max(8, round(rotated_low.get_height() * pixel_scale))
        pixel_circle = pygame.transform.scale(rotated_low, (scaled_w, scaled_h))
        pixel_circle.set_alpha(round(255 * inc_progress))
        circle_rect = pixel_circle.get_rect(center=(round(self.origin_x), round(self.y)))
        screen.blit(pixel_circle, circle_rect)


class HeatWave:
    """Descending sky-drop heat wave spanning the arena with a safe gap for the player."""

    def __init__(
        self,
        arena_width,
        gap_x,
        gap_width=160,
        height=96,
        fall_speed=460.0,
        telegraph_duration=0.65,
        damage=1,
    ):
        self.arena_width = max(300, int(arena_width))
        self.gap_width = int(gap_width)
        self.gap_x = max(40, min(int(gap_x), self.arena_width - self.gap_width - 40))
        self.height = int(height)
        self.y = 12.0
        self.fall_speed = float(fall_speed)
        self.telegraph_duration = float(telegraph_duration)
        self.age = 0.0
        self.damage = damage
        self.active = True
        self.has_damaged_player = False

        tile = load_heat_wave_surface()
        if tile.get_height() != self.height:
            tile = pygame.transform.scale(tile, (tile.get_width(), self.height))
        tile_w = tile.get_width()

        # Build left segment surface & mask (0 .. gap_x)
        self.left_width = max(0, self.gap_x)
        self.left_surface = pygame.Surface((max(1, self.left_width), self.height), pygame.SRCALPHA)
        for tx in range(0, self.left_width, tile_w):
            self.left_surface.blit(tile, (tx, 0))
        self.left_mask = pygame.mask.from_surface(self.left_surface)

        # Build right segment surface & mask (gap_x + gap_width .. arena_width)
        self.right_x = self.gap_x + self.gap_width
        self.right_width = max(0, self.arena_width - self.right_x)
        self.right_surface = pygame.Surface((max(1, self.right_width), self.height), pygame.SRCALPHA)
        for tx in range(0, self.right_width, tile_w):
            self.right_surface.blit(tile, (tx, 0))
        self.right_mask = pygame.mask.from_surface(self.right_surface)

    @property
    def dropping(self):
        return self.age >= self.telegraph_duration

    @property
    def alpha(self):
        if self.telegraph_duration <= 0:
            return 255
        return min(255, max(0, round(255 * min(1.0, self.age / self.telegraph_duration))))

    @property
    def left_rect(self):
        return pygame.Rect(0, round(self.y), self.left_width, self.height)

    @property
    def right_rect(self):
        return pygame.Rect(self.right_x, round(self.y), self.right_width, self.height)

    @property
    def gap_rect(self):
        return pygame.Rect(self.gap_x, round(self.y), self.gap_width, self.height)

    def update(self, dt, floor_y):
        if not self.active:
            return
        self.age += dt
        if self.age >= self.telegraph_duration:
            self.y += self.fall_speed * dt
            if self.y >= floor_y:
                self.active = False

    def check_hit(self, player):
        """Return True if the descending heat wave hits the player (standing in the gap is safe)."""
        if not self.active or self.has_damaged_player or not self.dropping:
            return False

        p_rect = player.rect
        p_mask = getattr(player, "body_mask", None)
        if p_mask is None:
            p_mask = pygame.mask.Mask(p_rect.size, fill=True)

        # Check left segment
        if self.left_width > 0 and self.left_rect.colliderect(p_rect):
            offset = (p_rect.x - self.left_rect.x, p_rect.y - self.left_rect.y)
            if self.left_mask.overlap(p_mask, offset) is not None:
                self.has_damaged_player = True
                return True

        # Check right segment
        if self.right_width > 0 and self.right_rect.colliderect(p_rect):
            offset = (p_rect.x - self.right_rect.x, p_rect.y - self.right_rect.y)
            if self.right_mask.overlap(p_mask, offset) is not None:
                self.has_damaged_player = True
                return True

        return False

    def draw(self, screen):
        if not self.active:
            return

        current_alpha = self.alpha
        if self.left_width > 0:
            left_copy = self.left_surface.copy()
            left_copy.set_alpha(current_alpha)
            screen.blit(left_copy, self.left_rect)

        if self.right_width > 0:
            right_copy = self.right_surface.copy()
            right_copy.set_alpha(current_alpha)
            screen.blit(right_copy, self.right_rect)


class Fireball:
    def __init__(
        self,
        x,
        y,
        vx=0.0,
        vy=0.0,
        damage=1,
        launch_delay=0.0,
        speed=520.0,
        phase=0.0,
        oscillation_amplitude=28.0,
        oscillation_frequency=10.0,
        facing=-1,
        fade_duration=0.45,
    ):
        self.anchor_x = float(x)
        self.anchor_y = float(y)
        self.base_x = float(x)
        self.base_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.speed = float(speed)
        self.damage = damage
        self.active = True

        self.launch_delay = float(launch_delay)
        self.launched = self.launch_delay <= 0.0
        self.age = 0.0
        self.flight_time = 0.0
        self.phase = float(phase)
        self.linger_amplitude = 10.0
        self.oscillation_amplitude = float(oscillation_amplitude)
        self.oscillation_frequency = float(oscillation_frequency)
        self.facing = facing
        self.fade_duration = float(fade_duration)

        self._base_surf = load_fireball_surface()
        self.image = self._base_surf
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)
        if self.launched:
            self._orient_sprite()

    @property
    def spawn_progress(self):
        if self.fade_duration <= 0 or self.launched:
            return 1.0
        return min(1.0, max(0.0, self.age / self.fade_duration))

    @property
    def alpha(self):
        return round(255 * self.spawn_progress)

    def _orient_sprite(self):
        angle_deg = math.degrees(math.atan2(self.vy, -self.vx))
        if self.vx > 0:
            flipped = pygame.transform.flip(self._base_surf, True, False)
            angle_deg = math.degrees(math.atan2(-self.vy, self.vx))
            self.image = pygame.transform.rotate(flipped, angle_deg)
        else:
            self.image = pygame.transform.rotate(self._base_surf, angle_deg)

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)

    def launch_towards(self, target_x=None, target_y=None):
        self.launched = True
        self.flight_time = 0.0
        self.base_x = self.x
        self.base_y = self.y

        if target_x is not None and target_y is not None:
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            if dist > 1e-4:
                self.vx = (dx / dist) * self.speed
                self.vy = (dy / dist) * self.speed
            else:
                self.vx = self.facing * self.speed
                self.vy = 0.0
        elif abs(self.vx) < 1e-4 and abs(self.vy) < 1e-4:
            self.vx = self.facing * self.speed
            self.vy = 0.0

        self._orient_sprite()

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt, floor_y, player=None):
        if not self.active:
            return

        self.age += dt

        if not self.launched:
            # Linger in place and oscillate gently before launching sequentially
            self.x = self.anchor_x
            self.y = self.anchor_y + math.sin(
                self.age * self.oscillation_frequency + self.phase
            ) * self.linger_amplitude

            if self.age >= self.launch_delay:
                if player is not None:
                    self.launch_towards(player.rect.centerx, player.rect.centery)
                else:
                    self.launch_towards()
            return

        # Advance along primary trajectory and oscillate perpendicular to flight direction
        self.flight_time += dt
        self.base_x += self.vx * dt
        self.base_y += self.vy * dt

        speed_mag = math.hypot(self.vx, self.vy)
        if speed_mag > 1e-4:
            perp_x = -self.vy / speed_mag
            perp_y = self.vx / speed_mag
        else:
            perp_x, perp_y = 0.0, 1.0

        wave_offset = (
            math.sin(self.flight_time * self.oscillation_frequency + self.phase)
            * self.oscillation_amplitude
        )
        self.x = self.base_x + perp_x * wave_offset
        self.y = self.base_y + perp_y * wave_offset

        if (
            self.x + self.width < -200
            or self.x > 3000
            or self.base_y + self.height >= floor_y + 60
            or self.y < -400
        ):
            self.active = False

    def draw(self, screen):
        if not self.active:
            return
        progress = self.spawn_progress
        if progress < 1.0:
            scale = 0.35 + 0.65 * progress
            scaled_w = max(4, round(self.width * scale))
            scaled_h = max(4, round(self.height * scale))
            sprite = pygame.transform.scale(self.image, (scaled_w, scaled_h))
            sprite.set_alpha(self.alpha)
            dest = sprite.get_rect(center=self.rect.center)
            screen.blit(sprite, dest)
        else:
            screen.blit(self.image, self.rect)


def load_boss_animations(path):
    abs_path = os.path.abspath(path)
    cache_key = (abs_path, FRAME_WIDTH, FRAME_HEIGHT)
    if cache_key in _CACHED_BOSS_DATA:
        return _CACHED_BOSS_DATA[cache_key]["animations"]

    sheet = pygame.image.load(abs_path)
    if pygame.display.get_surface() is not None:
        sheet = sheet.convert_alpha()

    raw_width = 288
    raw_height = 160

    row_info = {
        "row_1": (0, 6),     # idle
        "row_2": (160, 12),  # walk
        "row_3": (320, 15),  # cleave attack
        "row_4": (480, 5),   # hit
        "row_5": (640, 22),  # death
    }

    animations = {}
    animations_right = {}
    full_masks_left = {}
    full_masks_right = {}
    body_masks_left = {}
    body_masks_right = {}
    attack_masks_left = {}
    attack_masks_right = {}

    body_rect_left = pygame.Rect(BODY_OFFSET_X_LEFT, BODY_OFFSET_Y, BODY_WIDTH, BODY_HEIGHT)
    body_rect_right = pygame.Rect(BODY_OFFSET_X_RIGHT, BODY_OFFSET_Y, BODY_WIDTH, BODY_HEIGHT)
    atk_rect_left = pygame.Rect(ATTACK_OFFSET_X_LEFT, ATTACK_OFFSET_Y, ATTACK_WIDTH, ATTACK_HEIGHT)
    atk_rect_right = pygame.Rect(ATTACK_OFFSET_X_RIGHT, ATTACK_OFFSET_Y, ATTACK_WIDTH, ATTACK_HEIGHT)

    for name, (start_y, frame_count) in row_info.items():
        frames_l = []
        frames_r = []
        f_masks_l = []
        f_masks_r = []
        b_masks_l = []
        b_masks_r = []
        a_masks_l = []
        a_masks_r = []

        for i in range(frame_count):
            x = i * raw_width
            height = min(raw_height, sheet.get_height() - start_y)

            raw_frame = sheet.subsurface(pygame.Rect(x, start_y, raw_width, height)).copy()
            frame_l = pygame.transform.scale(raw_frame, (FRAME_WIDTH, FRAME_HEIGHT))
            frame_r = pygame.transform.flip(frame_l, True, False)

            frames_l.append(frame_l)
            frames_r.append(frame_r)

            f_masks_l.append(pygame.mask.from_surface(frame_l))
            f_masks_r.append(pygame.mask.from_surface(frame_r))

            body_surf_l = frame_l.subsurface(body_rect_left)
            body_surf_r = frame_r.subsurface(body_rect_right)
            b_masks_l.append(pygame.mask.from_surface(body_surf_l))
            b_masks_r.append(pygame.mask.from_surface(body_surf_r))

            atk_surf_l = frame_l.subsurface(atk_rect_left)
            atk_surf_r = frame_r.subsurface(atk_rect_right)
            a_masks_l.append(pygame.mask.from_surface(atk_surf_l))
            a_masks_r.append(pygame.mask.from_surface(atk_surf_r))

        animations[name] = frames_l
        animations_right[name] = frames_r
        full_masks_left[name] = f_masks_l
        full_masks_right[name] = f_masks_r
        body_masks_left[name] = b_masks_l
        body_masks_right[name] = b_masks_r
        attack_masks_left[name] = a_masks_l
        attack_masks_right[name] = a_masks_r

    _CACHED_BOSS_DATA[cache_key] = {
        "animations": animations,
        "animations_right": animations_right,
        "full_masks_left": full_masks_left,
        "full_masks_right": full_masks_right,
        "body_masks_left": body_masks_left,
        "body_masks_right": body_masks_right,
        "attack_masks_left": attack_masks_left,
        "attack_masks_right": attack_masks_right,
    }
    return animations


class Boss:
    def __init__(self, x, y, audio=None):
        self.x = float(x)
        self.y = float(y)

        # Tight standing body hitbox dimensions (matches visible body inside the scaled sprite)
        self.width = BODY_WIDTH
        self.height = BODY_HEIGHT

        assets_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "assets",
                "boss",
                "boss_spritesheet.png",
            )
        )

        self.animations = load_boss_animations(assets_path)
        cache = _CACHED_BOSS_DATA[(assets_path, FRAME_WIDTH, FRAME_HEIGHT)]
        self.animations_right = cache["animations_right"]
        self.full_masks_left = cache["full_masks_left"]
        self.full_masks_right = cache["full_masks_right"]
        self.body_masks_left = cache["body_masks_left"]
        self.body_masks_right = cache["body_masks_right"]
        self.attack_masks_left = cache["attack_masks_left"]
        self.attack_masks_right = cache["attack_masks_right"]

        # Facing direction: -1 = left (default sprite orientation), 1 = right
        self.facing = -1
        self.audio = audio

        self.current_animation = "row_1"
        self.animation_index = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.10
        self.image = self.animations["row_1"][0]

        # Vertical physics only (boss stays stationary horizontally)
        self.velocity_y = 0.0
        self.gravity = 1300.0

        # Combat & melee attack state
        self.max_health = 250
        self.health = self.max_health
        self.damage_flash_timer = 0.0
        self.attack_damage = 1
        self.attack_range = float(ATTACK_WIDTH)
        self.attack_cooldown = 1.5
        self.attack_cooldown_duration = 2.0
        self.attack_id = 0
        self.last_hit_attack_id = -1
        self.attack_hit = False

        # Ranged fireball (temperature > 26 C) & sky-drop heat wave state
        self.fireballs = []
        self.fireball_speed = 520.0
        self.fireball_damage = 1
        self.fireball_volley_count = 5
        self.fireball_linger_base = 0.75
        self.fireball_launch_interval = 0.35
        self.fireball_cooldown = 0.8
        self.fireball_cooldown_duration = 6.5

        self.heat_waves = []
        self.heat_wave_gap_width = 170
        self.heat_wave_cooldown = 2.0
        self.heat_wave_cooldown_duration = 4.5

        # Incantation + straight horizontal laser state (when not in fire mode & player out of melee range)
        self.lasers = []
        self.laser_cooldown = 1.2
        self.laser_cooldown_duration = 3.0
        self.last_laser_height_index = -1

        self.colour = (180, 70, 70)

    @property
    def rect(self):
        """Tight world-space body hitbox of the boss."""
        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.width,
            self.height,
        )

    @property
    def hitbox(self):
        return self.rect

    @property
    def draw_rect(self):
        """World-space rect where the sprite surface is drawn so the body aligns with self.rect."""
        offset_x = BODY_OFFSET_X_LEFT if self.facing == -1 else BODY_OFFSET_X_RIGHT
        return pygame.Rect(
            round(self.x) - offset_x,
            round(self.y) - BODY_OFFSET_Y,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    @property
    def mask(self):
        """Full pygame.mask.Mask for the current animation frame and facing direction."""
        masks = self.full_masks_left if self.facing == -1 else self.full_masks_right
        return masks[self.current_animation][self.animation_index]

    @property
    def body_mask(self):
        """Tight pygame.mask.Mask for the boss's standing body region (aligned with self.rect)."""
        masks = self.body_masks_left if self.facing == -1 else self.body_masks_right
        return masks[self.current_animation][self.animation_index]

    @property
    def is_attack_active(self):
        """True during the active cleave slash frames (9..12) of row_3."""
        return (
            self.health > 0
            and self.current_animation == "row_3"
            and self.animation_index in ACTIVE_ATTACK_FRAMES
        )

    @property
    def attack_rect(self):
        """World-space bounding rect of the boss's cleaver slash during active attack frames."""
        if not self.is_attack_active:
            return None

        if self.facing == -1:
            atk_x = round(self.x) - ATTACK_WIDTH
        else:
            atk_x = round(self.x) + self.width

        atk_y = round(self.y) + (ATTACK_OFFSET_Y - BODY_OFFSET_Y)
        return pygame.Rect(atk_x, atk_y, ATTACK_WIDTH, ATTACK_HEIGHT)

    @property
    def attack_mask(self):
        """pygame.mask.Mask for the boss's cleaver hitbox during active attack frames."""
        if not self.is_attack_active:
            return None
        masks = self.attack_masks_left if self.facing == -1 else self.attack_masks_right
        return masks[self.current_animation][self.animation_index]

    def start_attack(self):
        """Trigger the boss's cleave attack animation (row_3)."""
        if self.health <= 0:
            return
        self.current_animation = "row_3"
        self.animation_index = 0
        self.animation_timer = 0.0
        self.attack_id += 1
        self.attack_hit = False
        self.attack_cooldown = self.attack_cooldown_duration
        if self.audio is not None:
            self.audio.play("boss_attack")
        self._sync_image()

    def shoot_fireball(self, target_x=None, target_y=None):
        """Spawn a volley of 5 fireballs at once that linger and then fire sequentially at the player."""
        if self.health <= 0:
            return []

        base_x = self.rect.left - 50 if self.facing == -1 else self.rect.right + 10
        center_y = self.rect.top + self.height * 0.42

        # Fan/arc offsets for the 5 summoned fireballs
        offsets = [
            (-20, -110),
            (-45, -55),
            (-55, 0),
            (-45, 55),
            (-20, 110),
        ]

        spawned = []
        for idx in range(self.fireball_volley_count):
            ox, oy = offsets[idx % len(offsets)]
            spawn_x = base_x + (ox if self.facing == -1 else -ox)
            spawn_y = center_y + oy
            launch_delay = self.fireball_linger_base + idx * self.fireball_launch_interval

            fb = Fireball(
                spawn_x,
                spawn_y,
                vx=self.facing * self.fireball_speed,
                vy=0.0,
                damage=self.fireball_damage,
                launch_delay=launch_delay,
                speed=self.fireball_speed,
                phase=idx * (math.pi / 2.5),
                facing=self.facing,
            )
            self.fireballs.append(fb)
            spawned.append(fb)

        self.fireball_cooldown = self.fireball_cooldown_duration
        return spawned

    def spawn_heat_wave(self, gap_x=None, arena_width=None):
        """Spawn a descending heat wave from the sky with a safe gap for the player."""
        if self.health <= 0:
            return None

        if arena_width is None:
            arena_width = max(600, round(self.x + self.width))

        # Place the safe gap in front of the boss (0 .. self.rect.left) so the player can reach it
        playable_right = max(260, round(self.x) - self.heat_wave_gap_width - 20)
        if gap_x is None:
            gap_x = random.randint(40, playable_right)
        else:
            gap_x = max(40, min(int(gap_x), max(40, arena_width - self.heat_wave_gap_width - 40)))

        hw = HeatWave(
            arena_width=arena_width,
            gap_x=gap_x,
            gap_width=self.heat_wave_gap_width,
            damage=self.fireball_damage,
        )
        self.heat_waves.append(hw)
        self.heat_wave_cooldown = self.heat_wave_cooldown_duration
        return hw

    def spawn_laser_incantation(self, floor_y, y=None):
        """Spawn an incantation circle that fires a straight horizontal laser at a different height each time."""
        if self.health <= 0:
            return None

        # Distinct vertical heights above the floor (low ground jump, mid-low, mid-high, high aerial)
        height_offsets = [32, 92, 152, 215]
        available_indices = [
            idx for idx in range(len(height_offsets)) if idx != self.last_laser_height_index
        ]
        chosen_index = random.choice(available_indices)
        self.last_laser_height_index = chosen_index

        if y is None:
            jitter = random.randint(-10, 10)
            laser_y = floor_y - height_offsets[chosen_index] + jitter
        else:
            laser_y = float(y)

        origin_x = self.rect.left - 30 if self.facing == -1 else self.rect.right + 30
        laser = LaserIncantation(
            origin_x=origin_x,
            y=laser_y,
            facing=self.facing,
            damage=self.attack_damage,
        )
        self.lasers.append(laser)
        self.laser_cooldown = self.laser_cooldown_duration
        return laser

    def check_attack_hit(self, player):
        """Check whether the boss's active attack mask overlaps the player's mask."""
        if not self.is_attack_active or self.attack_id == self.last_hit_attack_id:
            return False

        atk_rect = self.attack_rect
        atk_mask = self.attack_mask
        if atk_rect is None or atk_mask is None:
            return False

        player_rect = player.rect
        if not atk_rect.colliderect(player_rect):
            return False

        player_mask = getattr(player, "body_mask", None)
        if player_mask is None:
            player_mask = pygame.mask.Mask(player_rect.size, fill=True)

        offset = (player_rect.x - atk_rect.x, player_rect.y - atk_rect.y)
        if atk_mask.overlap(player_mask, offset) is not None:
            self.last_hit_attack_id = self.attack_id
            self.attack_hit = True
            return True

        return False

    def _sync_image(self):
        frames = self.animations if self.facing == -1 else self.animations_right
        self.image = frames[self.current_animation][self.animation_index]

    def set_animation(self, animation):
        if animation != self.current_animation:
            self.current_animation = animation
            self.animation_index = 0
            self.animation_timer = 0.0
            self._sync_image()

    def animate(self, dt):
        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            frames = self.animations[self.current_animation]
            self.animation_index += 1

            if self.animation_index >= len(frames):
                if self.current_animation == "row_5":
                    # Stay on final death frame
                    self.animation_index = len(frames) - 1
                elif self.current_animation in ("row_3", "row_4"):
                    # Return to idle and start the post-attack cooldown pause
                    if (
                        self.current_animation == "row_3"
                        and not self.attack_hit
                        and self.audio is not None
                    ):
                        self.audio.play("boss_miss")
                    self.current_animation = "row_1"
                    self.animation_index = 0
                    self.attack_cooldown = self.attack_cooldown_duration
                else:
                    self.animation_index = 0

            self._sync_image()

    def update(self, dt, floor_y, player=None, temperature=None):
        self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        if self.current_animation not in ("row_3", "row_4"):
            self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

        # Update active fireballs (lingering & oscillating flight) and heat waves
        for fireball in self.fireballs:
            fireball.update(dt, floor_y, player=player)
        self.fireballs = [fb for fb in self.fireballs if fb.active]

        for hw in self.heat_waves:
            hw.update(dt, floor_y)
        self.heat_waves = [hw for hw in self.heat_waves if hw.active]

        for laser in self.lasers:
            laser.update(dt)
        self.lasers = [ls for ls in self.lasers if ls.active]

        # Apply vertical gravity
        self.velocity_y += self.gravity * dt
        self.y += self.velocity_y * dt

        # Floor collision
        if self.y + self.height >= floor_y:
            self.y = floor_y - self.height
            self.velocity_y = 0.0

        if self.health <= 0:
            self.set_animation("row_5")
            self.animate(dt)
            return

        # Both the sky-drop heat wave and the 5-fireball volley only happen when temperature > 26 C,
        # and neither requires the player to be near the boss
        if _is_over_fireball_temp(temperature):
            if not self.heat_waves:
                self.heat_wave_cooldown = max(0.0, self.heat_wave_cooldown - dt)
                if self.heat_wave_cooldown <= 0:
                    self.spawn_heat_wave(arena_width=max(600, round(self.x + self.width)))

            if not self.fireballs:
                self.fireball_cooldown = max(0.0, self.fireball_cooldown - dt)
                if self.fireball_cooldown <= 0:
                    if player is not None:
                        self.shoot_fireball(player.rect.centerx, player.rect.centery)
                    else:
                        self.shoot_fireball()

        # Stationary boss melee & normal-temperature ranged laser AI
        if player is not None:
            if self.facing == -1:
                horizontal_gap = self.rect.left - player.rect.right
            else:
                horizontal_gap = player.rect.left - self.rect.right

            if self.current_animation not in ("row_3", "row_4"):
                if horizontal_gap <= self.attack_range and self.attack_cooldown <= 0:
                    self.start_attack()
                else:
                    self.set_animation("row_1")

            # When NOT in fire mode (temp <= 26) and player is outside melee range, cast incantation laser
            if (
                not _is_over_fireball_temp(temperature)
                and horizontal_gap > self.attack_range
                and not self.lasers
            ):
                self.laser_cooldown = max(0.0, self.laser_cooldown - dt)
                if self.laser_cooldown <= 0:
                    self.spawn_laser_incantation(floor_y)

        self.animate(dt)

    def take_damage(self, damage):
        if self.health <= 0:
            return
        self.health = max(0, self.health - damage)
        self.damage_flash_timer = 0.15
        if self.health <= 0:
            self.set_animation("row_5")
            self.fireballs.clear()
            self.heat_waves.clear()
            self.lasers.clear()

    def draw(self, screen):
        frame = self.image
        if self.damage_flash_timer > 0:
            frame = frame.copy()
            frame.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)

        screen.blit(frame, self.draw_rect)

        for hw in self.heat_waves:
            hw.draw(screen)

        for laser in self.lasers:
            laser.draw(screen)

        for fireball in self.fireballs:
            fireball.draw(screen)
