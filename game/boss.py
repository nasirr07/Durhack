import os
import pygame

_CACHED_BOSS_DATA = {}

# Scale factor relative to the base 450x270 frame (720x432 total frame, 200x283 visible boss body)
BOSS_SCALE = 1.6

FRAME_WIDTH = round(450 * BOSS_SCALE)                 # 720
FRAME_HEIGHT = round(270 * BOSS_SCALE)                # 432
BODY_OFFSET_X_LEFT = round(166 * BOSS_SCALE)          # 266
BODY_OFFSET_Y = round(92 * BOSS_SCALE)                # 147
BODY_WIDTH = round(125 * BOSS_SCALE)                  # 200
BODY_HEIGHT = FRAME_HEIGHT - BODY_OFFSET_Y - 2        # 283
BODY_OFFSET_X_RIGHT = FRAME_WIDTH - BODY_OFFSET_X_LEFT - BODY_WIDTH  # 254

# Cleaver slash region in front of the boss during row_3 active frames (9..12)
ATTACK_OFFSET_X_LEFT = round(32 * BOSS_SCALE)         # 51
ATTACK_OFFSET_Y = round(97 * BOSS_SCALE)              # 155
ATTACK_WIDTH = BODY_OFFSET_X_LEFT - ATTACK_OFFSET_X_LEFT  # 215
ATTACK_HEIGHT = FRAME_HEIGHT - ATTACK_OFFSET_Y - 2    # 275
ATTACK_OFFSET_X_RIGHT = FRAME_WIDTH - ATTACK_OFFSET_X_LEFT - ATTACK_WIDTH
ACTIVE_ATTACK_FRAMES = (9, 10, 11, 12)


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
    def __init__(self, x, y):
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

        self.current_animation = "row_1"
        self.animation_index = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.10
        self.image = self.animations["row_1"][0]

        # Vertical physics only (boss stays stationary horizontally)
        self.velocity_y = 0.0
        self.gravity = 1300.0

        # Combat & attack state
        self.max_health = 100
        self.health = self.max_health
        self.damage_flash_timer = 0.0
        self.attack_damage = 1
        self.attack_range = float(ATTACK_WIDTH)
        self.attack_cooldown = 1.0
        self.attack_cooldown_duration = 1.8
        self.attack_id = 0
        self.last_hit_attack_id = -1

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
        self.attack_cooldown = self.attack_cooldown_duration
        self._sync_image()

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
                    # Return to idle after finishing an attack or hit-react
                    self.current_animation = "row_1"
                    self.animation_index = 0
                else:
                    self.animation_index = 0

            self._sync_image()

    def update(self, dt, floor_y, player=None):
        self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

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

        # Stationary boss AI: never moves horizontally, attacks when player is in range
        if player is not None:
            if self.current_animation not in ("row_3", "row_4"):
                if self.facing == -1:
                    horizontal_gap = self.rect.left - player.rect.right
                else:
                    horizontal_gap = player.rect.left - self.rect.right

                if horizontal_gap <= self.attack_range and self.attack_cooldown <= 0:
                    self.start_attack()
                else:
                    self.set_animation("row_1")

        self.animate(dt)

    def take_damage(self, damage):
        if self.health <= 0:
            return
        self.health = max(0, self.health - damage)
        self.damage_flash_timer = 0.15
        if self.health <= 0:
            self.set_animation("row_5")

    def draw(self, screen):
        frame = self.image
        if self.damage_flash_timer > 0:
            frame = frame.copy()
            frame.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)

        screen.blit(frame, self.draw_rect)

        # Health bar centered over the boss's tight body rect
        bar_width = 240
        bar_height = 18
        health_percentage = self.health / self.max_health

        bar_x = self.rect.centerx - bar_width / 2
        bar_y = self.rect.top - 30

        pygame.draw.rect(
            screen,
            (70, 70, 70),
            (bar_x, bar_y, bar_width, bar_height),
        )

        pygame.draw.rect(
            screen,
            (220, 50, 50),
            (bar_x, bar_y, bar_width * health_percentage, bar_height),
        )
