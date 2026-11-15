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


if __name__ == "__main__":
    unittest.main()
