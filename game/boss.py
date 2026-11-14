import pygame


class Boss:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

        self.width = 300
        self.height = 300

        # Physics
        self.velocity_y = 0.0
        self.gravity = 1300.0

        # Health
        self.max_health = 100
        self.health = self.max_health

        self.colour = (180, 70, 70)

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x),
            round(self.y),
            self.width,
            self.height
        )

    def update(self, dt, floor_y):
        # Apply gravity
        self.velocity_y += self.gravity * dt
        self.y += self.velocity_y * dt

        # Floor collision
        if self.y + self.height >= floor_y:
            self.y = floor_y - self.height
            self.velocity_y = 0

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect)

        # Health bar
        bar_width = 200
        bar_height = 16

        health_percentage = self.health / self.max_health

        bar_x = self.x + self.width / 2 - bar_width / 2
        bar_y = self.y - 30

        pygame.draw.rect(
            screen,
            (70, 70, 70),
            (bar_x, bar_y, bar_width, bar_height)
        )

        pygame.draw.rect(
            screen,
            (220, 50, 50),
            (bar_x, bar_y, bar_width * health_percentage, bar_height)
        )