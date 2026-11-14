
import pygame

from collision import resolve_player_collisions


class Player:
    def __init__(self, x, y):

        # Health
        self.max_health = 5
        self.health = self.max_health

        # Position and dimensions
        self.x = float(x)
        self.y = float(y)

        self.width = 48
        self.height = 48

        # Velocity
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # Physics settings
        self.gravity = 1300.0
        self.jump_strength = -650.0
        self.move_speed = 350.0

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

    def update(self, dt, keys, screen_width, floor_y):
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
        if self.jump_buffer > 0 and self.coyote_time > 0:
            self.velocity_y = self.jump_strength
            self.grounded = False
            self.coyote_time = 0
            self.jump_buffer = 0

        # Horizontal movement / dash
        if self.dash_timer > 0:
            self.velocity_x = self.dash_direction * self.dash_speed
            self.dash_timer = max(0, self.dash_timer - dt)
        else:
            self.velocity_x = movement_x * self.move_speed

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

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.colour,
            self.rect
        )

    def take_damage(self, damage=1):
        self.health = max(0, self.health - damage)
