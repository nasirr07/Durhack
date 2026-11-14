from reader import SerialReader
import os
import pygame
import sys

from player import Player
from boss import Boss
from combat import CombatSystem
from collision import resolve_player_boss_collision
from animator import Animator
from spritesheet import SpriteSheet

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

# Data from serial port
serial_reader = SerialReader()
serial_reader.Start()


sheet_cutter = SpriteSheet()


def get_all_assets(assets_dir=None):
    if assets_dir is None:
        assets_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "assets")
        )

    def load_directory(directory_path):
        folder_dict = {}
        for entry in sorted(os.listdir(directory_path), key=str.lower):
            full_path = os.path.join(directory_path, entry)
            if os.path.isdir(full_path):
                folder_dict[entry] = load_directory(full_path)
            elif entry.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                stem = os.path.splitext(entry)[0]
                if stem.endswith("_spritesheet"):
                    key = stem.removesuffix("_spritesheet")
                    folder_dict[key] = sheet_cutter.get_sprites(
                        full_path, width=60, height=60, name=stem
                    )
                else:
                    img = pygame.image.load(full_path)
                    folder_dict[stem] = (
                        img.convert_alpha()
                        if pygame.display.get_surface()
                        else img
                    )
        return folder_dict

    return load_directory(assets_dir)


# Set animator assets
Animator.ASSETS = get_all_assets()


def build_background_surface(width, height):
    bg_surf = pygame.Surface((width, height))
    bg_surf.fill(BACKGROUND)
    map_assets = Animator.ASSETS.get("map", {})
    for i in range(1, 6):
        layer = map_assets.get(f"Background_{i}")
        if layer is not None:
            scaled = pygame.transform.scale(layer, (width, height))
            bg_surf.blit(scaled, (0, 0))
    return bg_surf.convert()


def build_floor_surface(width, height):
    floor_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    floor_surf.fill(FLOOR_COLOUR)
    tiles = Animator.ASSETS.get("map", {}).get("tiles", [])
    if tiles:
        ground_tile = pygame.transform.scale(tiles[0], (height, height))
        tile_w = ground_tile.get_width()
        for x in range(0, width, tile_w):
            floor_surf.blit(ground_tile, (x, 0))
    return floor_surf.convert_alpha()


background_surface = build_background_surface(SCREEN_WIDTH, FLOOR_Y)
floor_surface = build_floor_surface(SCREEN_WIDTH, FLOOR_HEIGHT)

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
    screen.blit(background_surface, (0, 0))

    # Floor
    screen.blit(floor_surface, (0, FLOOR_Y))

    # Game entities
    player.draw(screen)
    boss.draw(screen)

    draw_health(screen, player)

    # Instructions
    text = font.render(
        "A/D: Move | SPACE/W: Jump | LEFT SHIFT: Dash | J: Attack | ESC: Exit",
        True,
        WHITE
    )
    screen.blit(text, (30, 30))

    serial_data = serial_reader.GetSerialData()
    serial_text = font.render(
        f"Temp: {serial_data['temp']} | Light: {serial_data['light']} | Dir: {serial_data['dir']}",
        True,
        WHITE
    )
    screen.blit(serial_text, (30, 60))

    pygame.display.flip()

serial_reader.Stop()
pygame.quit()
sys.exit()
