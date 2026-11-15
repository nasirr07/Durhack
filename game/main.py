"""
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

# Fonts
title_font = pygame.font.Font(
    "assets/fonts/PressStart2P-Regular.ttf", 32
)

ui_font = pygame.font.Font(
    "assets/fonts/Silkscreen-Regular.ttf", 24
)

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


def draw_menu(screen):
    screen.fill(BACKGROUND)

    title_font = pygame.font.Font(None, 100)
    button_font = pygame.font.Font(None, 50)

    title = title_font.render("MICROROGUE", True, WHITE)
    screen.blit(
        title,
        (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3)
    )

    # Button rectangles
    play_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 120,
        SCREEN_HEIGHT // 2,
        240,
        70
    )

    exit_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 120,
        SCREEN_HEIGHT // 2 + 100,
        240,
        70
    )

    mouse_pos = pygame.mouse.get_pos()

    # Play button
    play_colour = (70, 180, 100) if play_button.collidepoint(mouse_pos) else (40, 130, 70)
    pygame.draw.rect(screen, play_colour, play_button, border_radius=12)

    play_text = button_font.render("PLAY", True, WHITE)
    screen.blit(play_text, play_text.get_rect(center=play_button.center))

    # Exit button
    exit_colour = (200, 70, 70) if exit_button.collidepoint(mouse_pos) else (140, 40, 40)
    pygame.draw.rect(screen, exit_colour, exit_button, border_radius=12)

    exit_text = button_font.render("EXIT", True, WHITE)
    screen.blit(exit_text, exit_text.get_rect(center=exit_button.center))

    pygame.display.flip()

    return play_button, exit_button

def draw_death_screen(screen):
    screen.fill((15, 10, 15))

    title_font = pygame.font.Font(None, 110)
    button_font = pygame.font.Font(None, 45)

    # Game Over title
    title = title_font.render("GAME OVER, YOU LOSE", True, (220, 50, 50))
    screen.blit(
        title,
        title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    )

    # Exit button
    exit_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 120,
        SCREEN_HEIGHT // 2 + 80,
        240,
        70
    )

    mouse_pos = pygame.mouse.get_pos()

    exit_colour = (
        (200, 70, 70)
        if exit_button.collidepoint(mouse_pos)
        else (140, 40, 40)
    )

    pygame.draw.rect(
        screen,
        exit_colour,
        exit_button,
        border_radius=12
    )

    exit_text = button_font.render("EXIT", True, WHITE)
    screen.blit(exit_text, exit_text.get_rect(center=exit_button.center))

    pygame.display.flip()

    return exit_button

def draw_victory_screen(screen):
    screen.fill((15, 10, 15))

    title_font = pygame.font.Font(None, 110)
    button_font = pygame.font.Font(None, 45)

    # Game Over title
    title = title_font.render("GAME OVER, YOU WIN!!", True, (220, 50, 50))
    screen.blit(
        title,
        title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    )

    # Exit button
    exit_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 120,
        SCREEN_HEIGHT // 2 + 80,
        240,
        70
    )

    mouse_pos = pygame.mouse.get_pos()

    exit_colour = (
        (200, 70, 70)
        if exit_button.collidepoint(mouse_pos)
        else (140, 40, 40)
    )

    pygame.draw.rect(
        screen,
        exit_colour,
        exit_button,
        border_radius=12
    )

    exit_text = button_font.render("EXIT", True, WHITE)
    screen.blit(exit_text, exit_text.get_rect(center=exit_button.center))

    pygame.display.flip()

    return exit_button
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
menu_running = True 

while menu_running and running:

    play_button, exit_button = draw_menu(screen)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            menu_running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                if play_button.collidepoint(event.pos):
                    menu_running = False

                elif exit_button.collidepoint(event.pos):
                    running = False
                    menu_running = False

    clock.tick(60)


while running and player.health > 0 and boss.health > 0:
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
    ) and player.boss_collision_started:
        player.take_damage(
            knockback_direction=player.boss_collision_direction
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

# Death screen
if running and player.health <= 0:

    death_screen_running = True

    while death_screen_running:

        exit_button = draw_death_screen(screen)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                death_screen_running = False
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if exit_button.collidepoint(event.pos):
                    death_screen_running = False
                    running = False

        clock.tick(60)

elif running and boss.health <= 0:
        victory_screen_running = True

        while victory_screen_running:

            exit_button = draw_victory_screen(screen)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    victory_screen_running = False
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if exit_button.collidepoint(event.pos):
                        victory_screen_running = False
                        running = False

        clock.tick(60)

serial_reader.Stop()
pygame.quit()
sys.exit()
"""

import os
import sys

import pygame

from animator import Animator
from reader import SerialReader
from screen_flow import ScreenController, ScreenState
from session import GameplaySession
from spritesheet import SpriteSheet
from ui import PALETTE, PixelUI
from weather import WeatherSystem


BACKGROUND = (25, 25, 30)
FLOOR_COLOUR = (90, 90, 100)
ASSETS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "assets")
)


def get_all_assets(assets_dir, sheet_cutter):
    def load_directory(directory_path):
        folder_dict = {}
        for entry in sorted(os.listdir(directory_path), key=str.lower):
            full_path = os.path.join(directory_path, entry)
            if os.path.isdir(full_path):
                folder_dict[entry] = load_directory(full_path)
            elif entry.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
                stem = os.path.splitext(entry)[0]
                if stem.endswith("_spritesheet"):
                    folder_dict[stem.removesuffix("_spritesheet")] = (
                        sheet_cutter.get_sprites(
                            full_path,
                            width=60,
                            height=60,
                            name=stem,
                        )
                    )
                else:
                    folder_dict[stem] = pygame.image.load(full_path).convert_alpha()
        return folder_dict

    return load_directory(assets_dir)


def build_background_surface(width, height):
    background = pygame.Surface((width, height))
    background.fill(BACKGROUND)
    map_assets = Animator.ASSETS.get("map", {})
    for index in range(1, 6):
        layer = map_assets.get(f"Background_{index}")
        if layer is not None:
            background.blit(pygame.transform.scale(layer, (width, height)), (0, 0))
    return background.convert()


def build_floor_surface(width, height):
    floor = pygame.Surface((width, height), pygame.SRCALPHA)
    floor.fill(FLOOR_COLOUR)
    tiles = Animator.ASSETS.get("map", {}).get("tiles", [])
    if tiles:
        ground_tile = pygame.transform.scale(tiles[0], (height, height))
        for x in range(0, width, ground_tile.get_width()):
            floor.blit(ground_tile, (x, 0))
    return floor.convert_alpha()


def draw_health(screen, player, font):
    for index in range(player.max_health):
        colour = PALETTE["ember"] if index < player.health else PALETTE["panel_light"]
        heart = font.render("♥", False, colour)
        screen.blit(heart, (24 + index * 34, 64))


def draw_gameplay(screen, session, background_surface, floor_surface, font, serial_data):
    shake_x, shake_y = session.hazard.shake_offset
    screen.blit(background_surface, (shake_x, shake_y))
    screen.blit(
        floor_surface,
        (shake_x, screen.get_height() - floor_surface.get_height() + shake_y),
    )
    if session.weather is not None:
        session.weather.draw(screen)
    world = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    session.player.draw(world)
    session.boss.draw(world)
    session.hazard.draw(world)
    screen.blit(world, (shake_x, shake_y))
    draw_health(screen, session.player, font)

    instructions = font.render(
        "A/D move   Space jump   Shift dash   J strike   Esc quit",
        False,
        PALETTE["cream"],
    )
    screen.blit(instructions, (24, 20))

    sensor_text = font.render(
        f"Temp: {serial_data['temp']}   Light: {serial_data['light']}   Dir: {serial_data['dir']}",
        False,
        PALETTE["muted"],
    )
    screen.blit(sensor_text, (24, 44))


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("MicroRogue")
    clock = pygame.time.Clock()

    width, height = screen.get_size()
    floor_height = 140
    floor_y = height - floor_height
    Animator.ASSETS = get_all_assets(ASSETS_DIR, SpriteSheet())
    background_surface = build_background_surface(width, floor_y)
    floor_surface = build_floor_surface(width, floor_height)
    weather_assets = Animator.ASSETS.get("Weather", {})
    weather = WeatherSystem(
        width,
        floor_y,
        weather_assets.get("PixelatedSun"),
    )

    ui = PixelUI((width, height), ASSETS_DIR)
    hud_font = pygame.font.Font(
        os.path.join(ASSETS_DIR, "Fonts", "Silkscreen-Regular.ttf"),
        max(14, min(width, height) // 55),
    )
    serial_reader = SerialReader()
    serial_reader.Start()
    session = GameplaySession(width, floor_y, weather)
    controller = ScreenController()
    running = True

    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        events = pygame.event.get()

        if controller.state == ScreenState.START:
            option_rects = ui.draw_start(
                screen,
                background_surface,
                floor_surface,
                controller.selected_index,
            )
            controller.set_option_rects(option_rects)
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    continue
                action = controller.handle_event(event)
                if action == "start":
                    controller.state = ScreenState.GAMEPLAY
                elif action == "quit":
                    running = False

        elif controller.state == ScreenState.GAMEPLAY:
            keys = pygame.key.get_pressed()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    session.handle_event(event)

            if running:
                serial_data = serial_reader.GetSerialData()
                session.update(
                    dt,
                    keys,
                    serial_data["dir"],
                    serial_data.get("temp"),
                )
                draw_gameplay(
                    screen,
                    session,
                    background_surface,
                    floor_surface,
                    hud_font,
                    serial_data,
                )
                if session.player.health <= 0 or session.boss.health <= 0:
                    controller.show_end_screen(session.boss.health <= 0)

        elif controller.state == ScreenState.END:
            option_rects = ui.draw_end(
                screen,
                background_surface,
                floor_surface,
                session,
                controller.victory,
                controller.selected_index,
            )
            controller.set_option_rects(option_rects)
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    continue
                action = controller.handle_event(event)
                if action == "restart":
                    session.reset()
                    controller.state = ScreenState.GAMEPLAY
                elif action == "menu":
                    session.reset()
                    controller.show_start_screen()

        pygame.display.flip()

    serial_reader.Stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
