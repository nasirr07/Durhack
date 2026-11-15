import unittest

import pygame

from session import GameplaySession


class GameplaySessionTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.session = GameplaySession(800, 600)

    def tearDown(self):
        pygame.quit()

    def test_reset_recreates_clean_gameplay_state(self):
        original_player = self.session.player
        self.session.player.health = 1
        self.session.player.attack_cooldown = 0.25
        self.session.player.damage_flash_timer = 0.4
        self.session.boss.health = 10

        self.session.reset()

        self.assertIsNot(self.session.player, original_player)
        self.assertEqual(self.session.player.health, self.session.player.max_health)
        self.assertEqual(self.session.player.attack_cooldown, 0)
        self.assertEqual(self.session.player.damage_flash_timer, 0)
        self.assertEqual(self.session.boss.health, self.session.boss.max_health)
        self.assertEqual(self.session.combat.last_hit_attack_id, -1)

    def test_update_passes_temperature_to_weather(self):
        readings = []

        class WeatherProbe:
            def update(self, dt, temperature):
                readings.append((dt, temperature))

        session = GameplaySession(800, 600, WeatherProbe())
        session.update(0.1, pygame.key.get_pressed(), "none", 26)

        self.assertEqual(readings, [(0.1, 26)])


if __name__ == "__main__":
    unittest.main()
