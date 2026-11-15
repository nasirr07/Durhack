from boss import Boss
from collision import resolve_player_boss_collision
from combat import CombatSystem
from player import Player


class GameplaySession:
    def __init__(self, screen_width, floor_y):
        self.screen_width = screen_width
        self.floor_y = floor_y
        self.reset()

    def reset(self):
        self.player = Player(150, self.floor_y - 48)
        self.boss = Boss(
            self.screen_width - 400,
            self.floor_y - 300,
        )
        self.combat = CombatSystem()

    def handle_event(self, event):
        self.player.handle_event(event)

    def update(self, dt, keys):
        self.player.update(dt, keys, self.screen_width, self.floor_y)
        self.boss.update(dt, self.floor_y)

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
