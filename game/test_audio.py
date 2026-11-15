import unittest
import tempfile

import pygame

from audio import GameAudio
from boss import Boss
from combat import CombatSystem
from player import Player


class AudioProbe:
    def __init__(self):
        self.events = []

    def play(self, name):
        self.events.append(name)


class AudioTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.keys = {
            pygame.K_a: False,
            pygame.K_LEFT: False,
            pygame.K_d: False,
            pygame.K_RIGHT: False,
        }

    def tearDown(self):
        pygame.quit()

    def press(self, player, key):
        player.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=key)
        )

    def test_player_attack_hit_and_dash_play_once(self):
        audio = AudioProbe()
        player = Player(100, 100, audio=audio)
        boss = type(
            "BossStub",
            (),
            {
                "rect": pygame.Rect(150, 100, 40, 40),
                "take_damage": lambda self, amount: None,
            },
        )()

        self.press(player, pygame.K_j)
        player.update(0.01, self.keys, 800, 600)
        self.assertEqual(audio.events, [])
        CombatSystem().update(player, boss)
        self.assertEqual(audio.events, ["player_attack_hit"])

        self.press(player, pygame.K_LSHIFT)
        player.update(0.01, self.keys, 800, 600)
        self.assertEqual(
            audio.events,
            ["player_attack_hit", "dash"],
        )

    def test_player_miss_plays_only_when_attack_expires_without_a_hit(self):
        audio = AudioProbe()
        player = Player(100, 100, audio=audio)

        self.press(player, pygame.K_j)
        player.update(0.01, self.keys, 800, 600)
        player.update(player.attack_duration, self.keys, 800, 600)

        self.assertEqual(audio.events, ["player_miss"])

    def test_player_hit_suppresses_miss_sound(self):
        audio = AudioProbe()
        player = Player(100, 100, audio=audio)

        self.press(player, pygame.K_j)
        player.update(0.01, self.keys, 800, 600)
        player.attack_hit = True
        player.update(player.attack_duration, self.keys, 800, 600)

        self.assertEqual(audio.events, [])

    def test_landing_after_a_jump_plays_walking_sound_once(self):
        audio = AudioProbe()
        player = Player(100, 500, audio=audio)
        player.grounded = True
        player.jumps_remaining = player.max_jumps

        self.press(player, pygame.K_SPACE)
        player.update(0.01, self.keys, 800, 600)
        for _ in range(100):
            player.update(0.02, self.keys, 800, 600)

        self.assertEqual(audio.events, ["walking"])

    def test_boss_attack_and_miss_events_play_once(self):
        audio = AudioProbe()
        boss = Boss.__new__(Boss)
        boss.health = 1
        boss.current_animation = "row_1"
        boss.animation_index = 0
        boss.animation_timer = 0.0
        boss.attack_id = 0
        boss.attack_cooldown_duration = 2.0
        boss.attack_cooldown = 0.0
        boss.audio = audio
        boss.animations = {"row_3": [object()], "row_1": [object()]}
        boss._sync_image = lambda: None

        boss.start_attack()
        self.assertEqual(audio.events, ["boss_attack"])

        boss.current_animation = "row_3"
        boss.animation_timer = boss.animation_speed = 0.1
        boss.animation_index = 0
        boss.attack_hit = False
        boss.animate(0.1)
        self.assertEqual(audio.events, ["boss_attack", "boss_miss"])

    def test_missing_audio_files_do_not_raise(self):
        with tempfile.TemporaryDirectory() as directory:
            audio = GameAudio(directory)
            audio.play("player_attack_hit")
            audio.start_gameplay_music()
            audio.stop_gameplay_music()


if __name__ == "__main__":
    unittest.main()
