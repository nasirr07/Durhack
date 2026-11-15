import pygame
import os 
def load_boss_animations(path):
    sheet = pygame.image.load(path).convert_alpha()
    print("Loaded sheet dimensions:", sheet.get_size())
    print("Visible pixels in whole sheet:",
        pygame.mask.from_surface(sheet).count())

    frame_width = 288
    frame_height = 160

    row_info = {
        "row_1": (0, 6),
        "row_2": (160, 12),
        "row_3": (320, 15),
        "row_4": (480, 5),
        "row_5": (640, 22)
    }
    animations = {}

    for name, (start_y, frame_count) in row_info.items():
        frames = []

        for i in range(frame_count):
            x = i * frame_width
            height = min(frame_height, sheet.get_height() - start_y)

            frame = sheet.subsurface(
                pygame.Rect(x, start_y, frame_width, height)
            ).copy()

            print(
            f"{name}, frame {i}:",
            pygame.mask.from_surface(frame).count(),
            "visible pixels"
)

            frame = pygame.transform.scale(
                frame, (450, 270)
            )

            frames.append(frame)

        animations[name] = frames

    print("Boss animations loaded:")
    for name, frames in animations.items():
        print(name, len(frames), "frames")

    return animations

class Boss:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

        self.width = 450
        self.height = 270

        
        

    # Get the assets folder relative to this Python file
        assets_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "boss",
            "boss_spritesheet.png"
        )

        assets_path = os.path.abspath(assets_path)

        print("Loading boss spritesheet:", assets_path)

        self.animations = load_boss_animations(assets_path)

        self.current_animation = "row_1"
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.12

        self.image = self.animations["row_1"][0]

        print("Boss image size:", self.image.get_size())
        print("Visible pixels:", pygame.mask.from_surface(self.image).count())

        self.current_animation = "row_1"
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.12
        self.image = self.animations["row_1"][0]

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

    def set_animation(self, animation):

        if animation != self.current_animation:

            self.current_animation = animation
            self.animation_index = 0
            self.animation_timer = 0

            self.image = self.animations[animation][0]

    def animate(self, dt):
        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:    
            self.animation_timer = 0

            frames = self.animations[self.current_animation]

            self.animation_index += 1

            if self.animation_index >= len(frames):
                self.animation_index = 0

            self.image = frames[self.animation_index]

    def update(self, dt, floor_y):
        # Apply gravity
        self.velocity_y += self.gravity * dt
        self.y += self.velocity_y * dt

        # Floor collision
        if self.y + self.height >= floor_y:
            self.y = floor_y - self.height
            self.velocity_y = 0

        # Only animate when the boss is not idle
            self.animate(dt)

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

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
