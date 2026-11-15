import unittest

import pygame

from ui import BossHealthBar


class BossStub:
    max_health = 100
    health = 100


class BossHealthBarTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.font = pygame.font.Font(None, 18)
        self.bar = BossHealthBar((800, 600), self.font)
        self.boss = BossStub()

    def tearDown(self):
        pygame.quit()

    def test_full_health_fills_main_and_delayed_layers(self):
        self.bar.update(0.1, self.boss)
        self.assertEqual(self.bar.health_ratio, 1.0)
        self.assertEqual(self.bar.delayed_ratio, 1.0)

    def test_damage_updates_main_immediately_and_delayed_layer_catches_up(self):
        self.bar.update(0.1, self.boss)
        self.boss.health = 50
        self.bar.update(0.1, self.boss)

        self.assertEqual(self.bar.health_ratio, 0.5)
        self.assertGreater(self.bar.delayed_ratio, self.bar.health_ratio)

        self.bar.update(2.0, self.boss)
        self.assertEqual(self.bar.delayed_ratio, 0.5)

    def test_zero_health_clamps_to_empty(self):
        self.boss.health = -20
        self.bar.update(0.1, self.boss)
        self.assertEqual(self.bar.health_ratio, 0.0)

    def test_bar_is_bottom_centred(self):
        self.assertEqual(self.bar.rect.centerx, 400)
        self.assertGreater(self.bar.rect.bottom, 550)


if __name__ == "__main__":
    unittest.main()
