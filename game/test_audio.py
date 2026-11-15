import unittest
import tempfile

import pygame

from audio import GameAudio
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

    def test_player_attack_and_dash_play_once_when_started(self):
        audio = AudioProbe()
        player = Player(100, 100, audio=audio)

        self.press(player, pygame.K_j)
        player.update(0.01, self.keys, 800, 600)
        self.assertEqual(audio.events, ["player_attack"])

        self.press(player, pygame.K_LSHIFT)
        player.update(0.01, self.keys, 800, 600)
        self.assertEqual(
            audio.events,
            ["player_attack", "dash"],
        )

    def test_player_miss_plays_only_when_attack_expires_without_a_hit(self):
        audio = AudioProbe()
        player = Player(100, 100, audio=audio)

        self.press(player, pygame.K_j)
        player.update(0.01, self.keys, 800, 600)
        player.update(player.attack_duration, self.keys, 800, 600)

        self.assertEqual(
            audio.events,
            ["player_attack", "player_miss"],
        )

    def test_player_hit_suppresses_miss_sound(self):
        audio = AudioProbe()
        player = Player(100, 100, audio=audio)

        self.press(player, pygame.K_j)
        player.update(0.01, self.keys, 800, 600)
        player.attack_hit = True
        player.update(player.attack_duration, self.keys, 800, 600)

        self.assertEqual(audio.events, ["player_attack"])

    def test_missing_audio_files_do_not_raise(self):
        with tempfile.TemporaryDirectory() as directory:
            audio = GameAudio(directory)
            audio.play("player_attack")
            audio.start_gameplay_music()
            audio.stop_gameplay_music()


if __name__ == "__main__":
    unittest.main()
