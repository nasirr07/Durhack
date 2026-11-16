import os
import sys

import pygame

from animator import Animator
from reader import SerialReader
from screen_flow import ScreenController, ScreenState
from session import GameplaySession
from spritesheet import SpriteSheet
from taunts import BossTauntBox
from ui import BossHealthBar, PALETTE, PixelUI
from audio import GameAudio
from lighting import DarknessSystem
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


def draw_health(screen, player):
    weather_assets = Animator.ASSETS.get("Weather", {})
    full_heart = weather_assets["heart"]
    empty_heart = weather_assets["empty_heart"]

    for index in range(player.max_health):
        sprite = full_heart if index < player.health else empty_heart
        screen.blit(sprite, (24 + index * (sprite.get_width() + 8), 80))


def draw_gameplay(
    screen,
    session,
    background_surface,
    floor_surface,
    font,
    serial_data,
    lighting=None,
    boss_health_bar=None,
    taunt_box=None,
    dt=0.0,
):
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
    
    if lighting is not None:
        lighting.apply(
            screen,
            (
                session.player.rect.centerx + shake_x,
                session.player.rect.centery + shake_y,
            ),
            draw_entities=lambda surface: (
                session.boss.draw(surface),
                session.hazard.draw(surface),
            ),
            entity_offset=(shake_x, shake_y),
        )
    draw_health(screen, session.player)
    if boss_health_bar is not None:
        boss_health_bar.update(dt, session.boss)
        boss_health_bar.draw(screen)

    if taunt_box is not None:
        taunt_box.update(dt, session, serial_data)
        taunt_box.draw(screen)

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
    audio = GameAudio()
    wind_sound = audio.load_sound(
        "wind",
        os.path.join(ASSETS_DIR, "Weather", "wind_sound.wav"),
        volume=0.5,
    )
    
    width, height = screen.get_size()
    floor_height = 140
    floor_y = height - floor_height
    Animator.ASSETS = get_all_assets(ASSETS_DIR, SpriteSheet())
    background_surface = build_background_surface(width, floor_y)
    floor_surface = build_floor_surface(width, floor_height)
    weather_assets = Animator.ASSETS.get("Weather", {})
    heart_size = (32, 32)
    weather_assets["heart"] = pygame.transform.scale(weather_assets["heart"], heart_size)
    weather_assets["empty_heart"] = pygame.transform.scale(weather_assets["empty_heart"], heart_size)
    

    weather = WeatherSystem(
        width,
        floor_y,
        weather_assets.get("PixelatedSun"),
        wind_sound=wind_sound
    )
    lighting = DarknessSystem(screen.get_size())

    ui = PixelUI((width, height), ASSETS_DIR)
    boss_health_bar = BossHealthBar((width, height), ui.heading_font)
    taunt_box = BossTauntBox((width, height), ui.body_font, ui.small_font, audio=audio)
    hud_font = pygame.font.Font(
        os.path.join(ASSETS_DIR, "Fonts", "Silkscreen-Regular.ttf"),
        max(14, min(width, height) // 55),
    )
    serial_reader = SerialReader()
    serial_reader.Start()
    session = GameplaySession(width, floor_y, weather, audio=audio)
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
                    audio.start_gameplay_music()
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
                lighting.update(dt, serial_data.get("light"))
                draw_gameplay(
                    screen,
                    session,
                    background_surface,
                    floor_surface,
                    hud_font,
                    serial_data,
                    lighting,
                    boss_health_bar,
                    taunt_box,
                    dt,
                )
                if session.player.health <= 0 or session.boss.health <= 0:
                    audio.stop_gameplay_music()
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
                    taunt_box.reset()
                    audio.start_gameplay_music()
                    controller.state = ScreenState.GAMEPLAY
                elif action == "menu":
                    audio.stop_gameplay_music()
                    session.reset()
                    taunt_box.reset()
                    controller.show_start_screen()

        pygame.display.flip()

    audio.stop_gameplay_music()

    pygame.quit()

    serial_reader.Stop()
    sys.exit()


if __name__ == "__main__":
    main()
