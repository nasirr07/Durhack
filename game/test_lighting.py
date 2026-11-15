import unittest

import pygame

from lighting import DarknessSystem


class DarknessSystemTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.Surface((320, 240))
        self.lighting = DarknessSystem(self.screen.get_size(), visibility_radius=135)

    def tearDown(self):
        pygame.quit()

    def test_dark_sensor_smoothly_activates_and_light_disables_darkness(self):
        self.lighting.update(0.1, 0)
        self.assertGreater(self.lighting.intensity, 0.0)
        self.assertLess(self.lighting.intensity, 1.0)

        self.lighting.update(1.0, 0)
        self.assertEqual(self.lighting.intensity, 1.0)

        self.lighting.update(0.1, 100)
        self.assertGreater(self.lighting.intensity, 0.0)
        self.assertLess(self.lighting.intensity, 1.0)

    def test_invalid_sensor_values_leave_arena_lit(self):
        self.lighting.update(1.0, 0)
        self.lighting.update(0.1, None)
        self.assertLess(self.lighting.intensity, 1.0)

    def test_visibility_circle_preserves_player_area_and_darkens_outside(self):
        self.screen.fill((220, 220, 220))
        self.lighting.intensity = 1.0
        self.lighting.apply(self.screen, (160, 120))

        self.assertEqual(self.screen.get_at((160, 120))[:3], (220, 220, 220))
        self.assertLess(self.screen.get_at((10, 10))[0], 220)

    def test_entities_remain_dimly_visible_outside_visibility_circle(self):
        self.screen.fill((220, 220, 220))
        self.lighting.intensity = 1.0

        def draw_entities(surface):
            pygame.draw.rect(surface, (255, 0, 0), (10, 10, 20, 20))

        self.lighting.apply(
            self.screen,
            (160, 120),
            draw_entities=draw_entities,
        )

        pixel = self.screen.get_at((15, 15))
        self.assertGreater(pixel[0], 0)
        self.assertLess(pixel[0], 255)


if __name__ == "__main__":
    unittest.main()
