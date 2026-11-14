
import pygame
import sys

from player import Player
from boss import Boss
from combat import CombatSystem
from collision import resolve_player_boss_collision


pygame.init()

# Fullscreen settings
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

pygame.display.set_caption("MicroRogue")
clock = pygame.time.Clock()

# Colours
BACKGROUND = (25, 25, 30)
FLOOR_COLOUR = (90, 90, 100)
WHITE = (230, 230, 230)

# Environment
FLOOR_HEIGHT = 140
FLOOR_Y = SCREEN_HEIGHT - FLOOR_HEIGHT

# Create game objects
player = Player(150, FLOOR_Y - 48)

boss = Boss(
    SCREEN_WIDTH - 400,
    FLOOR_Y - 300
)

combat = CombatSystem()

# UI
font = pygame.font.Font(None, 28)


HEART_FONT = pygame.font.Font(None, 42)

def draw_health(screen, player):
    for i in range(player.max_health):
        if i < player.health:
            colour = (220, 50, 70)  # Red: full heart
        else:
            colour = (80, 80, 80)   # Grey: empty heart

        heart = HEART_FONT.render("♥", True, colour)
        screen.blit(heart, (30 + i * 40, 80))

# Game loop
running = True

while running:
    dt = min(clock.tick(60) / 1000, 0.05)

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            player.handle_event(event)

    # Input
    keys = pygame.key.get_pressed()

    # Update
    player.update(
        dt,
        keys,
        SCREEN_WIDTH,
        FLOOR_Y
    )

    boss.update(dt, FLOOR_Y)

    # Resolve Collisions
    if resolve_player_boss_collision(
        player,
        boss,
        SCREEN_WIDTH,
        FLOOR_Y
    ):
        knockback_direction = (
            -1 if player.rect.centerx < boss.rect.centerx else 1
        )
        player.take_damage(
            knockback_direction=knockback_direction
        )

    # Combat
    combat.update(player, boss)

    # Drawing
    screen.fill(BACKGROUND)
    

    # Floor
    pygame.draw.rect(
        screen,
        FLOOR_COLOUR,
        (0, FLOOR_Y, SCREEN_WIDTH, FLOOR_HEIGHT)
    )

    # Game entities
    player.draw(screen)
    boss.draw(screen)

    draw_health(screen, player)

    # Instructions
    text = font.render(
        "A/D: Move | SPACE/W: Jump | LEFT SHIFT: Dash | ESC: Exit",
        True,
        WHITE
    )

    screen.blit(text, (30, 30))

    pygame.display.flip()

pygame.quit()
sys.exit()
