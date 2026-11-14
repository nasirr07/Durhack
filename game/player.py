
import pygame
from collision import resolve_player_collisions
from animator import Animator


class Player:
    def __init__(self, x, y, animator=None):

        # Animator
        self.animator = animator if animator is not None else Animator()

        # Health
        self.max_health = 5
        self.health = self.max_health
        self.damage_cooldown = 0.0
        self.damage_cooldown_duration = 0.5
        self.damage_flash_timer = 0.0
        self.knockback_speed = 500.0
        self.knockback_deceleration = 700.0
        self.bounce_strength = -400.0
        self.knockback_timer = 0.0
        self.knockback_direction = 0
        self.knockback_velocity_x = 0.0

        # Light attack
        self.attack_requested = False
        self.attack_timer = 0.0
        self.attack_duration = 0.15
        self.attack_cooldown = 0.0
        self.attack_cooldown_duration = 0.3

        self.attack_range = 65
        self.attack_height = 35
        self.attack_damage = 10

        self.attack_id = 0

        # Position and dimensions
        self.x = float(x)
        self.y = float(y)

        self.width = 60
        self.height = 60

        # Velocity
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # Physics settings
        self.gravity = 1300.0
        self.jump_strength = -650.0
        self.move_speed = 350.0
        self.max_jumps = 2
        self.jumps_remaining = 0

        # Dash settings
        self.dash_speed = 900.0
        self.dash_duration = 0.15
        self.dash_cooldown_duration = 0.8

        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.dash_direction = 1
        self.dash_requested = False

        # Facing direction: 1 = right, -1 = left
        self.facing = 1

        # Jump reliability
        self.grounded = False
        self.coyote_time = 0.0
        self.jump_buffer = 0.0
        self.boss_collision_direction = 0
        self.boss_collision_started = False
        self.boss_contact_active = False

        self.coyote_duration = 0.12
        self.jump_buffer_duration = 0.12

        self.colour = (180, 180, 190)

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.width,
            self.height
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # Jump
            if event.key in (pygame.K_SPACE, pygame.K_w):
                self.jump_buffer = self.jump_buffer_duration

            # Dash
            if event.key == pygame.K_LSHIFT:
                self.dash_requested = True

            # Light attack
            if event.key == pygame.K_j:
                self.attack_requested = True

    def update(self, dt, keys, screen_width, floor_y):

        # Update attack timers
        self.attack_timer = max(0, self.attack_timer - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.damage_cooldown = max(0, self.damage_cooldown - dt)
        self.damage_flash_timer = max(0, self.damage_flash_timer - dt)
        self.knockback_timer = max(0, self.knockback_timer - dt)
        self.knockback_velocity_x = self._move_towards(
            self.knockback_velocity_x,
            0.0,
            self.knockback_deceleration * dt
        )

        # Start light attack
        if self.attack_requested and self.attack_cooldown <= 0:
            self.attack_timer = self.attack_duration
            self.attack_cooldown = self.attack_cooldown_duration
            self.attack_id += 1

        self.attack_requested = False

        # Horizontal input
        movement_x = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            movement_x -= 1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            movement_x += 1

        # Update facing direction
        if movement_x:
            self.facing = movement_x

        # Dash cooldown
        self.dash_cooldown = max(
            0,
            self.dash_cooldown - dt
        )

        # Start dash
        if (
            self.dash_requested
            and self.dash_cooldown <= 0
            and self.dash_timer <= 0
        ):
            self.dash_timer = self.dash_duration
            self.dash_cooldown = self.dash_cooldown_duration
            self.dash_direction = self.facing

        self.dash_requested = False

        # Coyote time
        if self.grounded:
            self.coyote_time = self.coyote_duration
        else:
            self.coyote_time = max(
                0,
                self.coyote_time - dt
            )

        # Jump buffer
        self.jump_buffer = max(
            0,
            self.jump_buffer - dt
        )

        # Jump
        can_ground_jump = (
            self.jump_buffer > 0
            and self.coyote_time > 0
            and self.jumps_remaining > 0
        )
        can_air_jump = (
            self.jump_buffer > 0
            and not self.grounded
            and self.jumps_remaining == 1
        )

        if can_ground_jump or can_air_jump:
            self.velocity_y = self.jump_strength
            self.grounded = False
            self.coyote_time = 0
            self.jump_buffer = 0
            self.jumps_remaining -= 1

        # Horizontal movement / dash
        if self.dash_timer > 0:
            movement_velocity_x = self.dash_direction * self.dash_speed
            self.dash_timer = max(0, self.dash_timer - dt)
        else:
            movement_velocity_x = movement_x * self.move_speed

        self.velocity_x = movement_velocity_x + self.knockback_velocity_x

        self.x += self.velocity_x * dt

        # Vertical physics
        self.velocity_y += self.gravity * dt
        self.y += self.velocity_y * dt

        # Resolve collisions
        resolve_player_collisions(
            self,
            screen_width,
            floor_y
        )

        # Update animation state and frame
        if self.animator is not None:
            self.animator.update(dt, player=self)

    def draw(self, screen):
        frame = self.animator.get_current_frame() if self.animator is not None else None
        is_flashing = (
            self.damage_flash_timer > 0
            and int(self.damage_flash_timer * 20) % 2 == 0
        )

        if frame is not None:
            if is_flashing:
                frame = frame.copy()
                frame.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
            dest = frame.get_rect(center=self.rect.center)
            screen.blit(frame, dest)
        else:
            colour = (255, 255, 255) if is_flashing else self.colour
            pygame.draw.rect(
                screen,
                colour,
                self.rect
            )
        # Draw light attack
        if self.attack_rect is not None:
            pygame.draw.rect(
                screen,
                (255, 220, 100),
                self.attack_rect,
                2
            )

    def take_damage(self, damage=1, knockback_direction=0):
        if self.damage_cooldown > 0:
            return False

        self.health = max(0, self.health - damage)
        self.damage_cooldown = self.damage_cooldown_duration
        self.damage_flash_timer = self.damage_cooldown_duration
        self.knockback_direction = knockback_direction
        self.knockback_velocity_x = knockback_direction * self.knockback_speed
        self.knockback_timer = (
            self.knockback_speed / self.knockback_deceleration
        )
        self.velocity_x = self.knockback_velocity_x
        self.velocity_y = self.bounce_strength
        return True

    @staticmethod
    def _move_towards(current, target, amount):
        if current < target:
            return min(current + amount, target)
        return max(current - amount, target)


    @property
    def attack_rect(self):
        if self.attack_timer <= 0:
            return None

        if self.facing == 1:
            attack_x = self.x + self.width
        else:
            attack_x = self.x - self.attack_range

        attack_y = self.y + (self.height - self.attack_height) / 2

        return pygame.Rect(
            round(attack_x),
            round(attack_y),
            self.attack_range,
            self.attack_height
        )
