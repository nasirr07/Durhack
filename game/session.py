from boss import Boss
from collision import resolve_player_boss_collision
from combat import CombatSystem
from hazards import EarthquakeHazard
from player import Player


class GameplaySession:
    def __init__(self, screen_width, floor_y, weather=None, audio=None):
        self.screen_width = screen_width
        self.floor_y = floor_y
        self.weather = weather
        self.audio = audio
        self.reset()

    def reset(self):
        self.player = Player(150, self.floor_y - 48, audio=self.audio)
        self.boss = Boss(
            self.screen_width - 390,
            self.floor_y - 495,
            audio=self.audio,
        )
        self.combat = CombatSystem()
        self.hazard = EarthquakeHazard(self.screen_width, self.floor_y)

    def handle_event(self, event):
        self.player.handle_event(event)

    def update(self, dt, keys, direction="none", temperature=None):
        self.player.update(dt, keys, self.screen_width, self.floor_y)
        self.boss.update(dt, self.floor_y, self.player, temperature)

        if resolve_player_boss_collision(
            self.player,
            self.boss,
            self.screen_width,
            self.floor_y,
        ) and self.player.boss_collision_started:
            self.player.take_damage(
                knockback_direction=self.player.boss_collision_direction
            )

        self.combat.update(self.player, self.boss)
        self.hazard.update(dt, direction, self.player)
        if self.weather is not None:
            self.weather.update(dt, temperature)
