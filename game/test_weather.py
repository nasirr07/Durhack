import unittest

import pygame

from weather import WeatherSystem


class WeatherSystemTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.sun = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.sun, (255, 190, 50), (16, 16), 12)
        self.weather = WeatherSystem(
            800,
            600,
            self.sun,
            seed=1,
        )

    def tearDown(self):
        pygame.quit()

    def test_only_temperatures_above_25_target_hot_weather(self):
        self.weather.update(0.1, 25)
        self.assertEqual(self.weather.hot_target, 0.0)
        self.weather.update(0.1, 26)
        self.assertEqual(self.weather.hot_target, 1.0)

    def test_clouds_are_generated_without_a_cloud_asset(self):
        self.assertEqual(len(self.weather.clouds), 6)
        self.assertTrue(
            all(cloud.sprite.get_at((0, 0)).a == 0 for cloud in self.weather.clouds)
        )

    def test_clouds_use_a_higher_smaller_sky_layout(self):
        self.assertLess(max(cloud.y for cloud in self.weather.clouds), 600 * 0.36)
        self.assertLess(max(cloud.width for cloud in self.weather.clouds), 800 * 0.20)

    def test_invalid_temperature_targets_default_cloudy_weather(self):
        self.weather.update(2.0, 30)
        self.assertEqual(self.weather.hot_intensity, 1.0)
        self.weather.update(0.1, "unknown")
        self.assertEqual(self.weather.hot_target, 0.0)
        self.assertLess(self.weather.hot_intensity, 1.0)

    def test_weather_transition_is_smooth_in_both_directions(self):
        self.weather.update(0.1, 30)
        self.assertGreater(self.weather.hot_intensity, 0.0)
        self.assertLess(self.weather.hot_intensity, 1.0)
        self.weather.update(2.0, 30)
        self.assertEqual(self.weather.hot_intensity, 1.0)
        self.weather.update(0.1, 25)
        self.assertGreater(self.weather.hot_intensity, 0.0)
        self.assertLess(self.weather.hot_intensity, 1.0)

    def test_clouds_move_and_wrap_at_left_edge(self):
        cloud = self.weather.clouds[0]
        start_x = cloud.x
        self.weather.update(0.5, 25)
        self.assertLess(cloud.x, start_x)
        cloud.x = -cloud.width - 1
        self.weather.update(0.0, 25)
        self.assertGreaterEqual(cloud.x, self.weather.width)

    def test_weather_draws_at_multiple_resolutions(self):
        for size in ((800, 600), (1280, 720)):
            weather = WeatherSystem(
                *size,
                self.sun,
                seed=1,
            )
            screen = pygame.Surface(size)
            weather.update(0.1, 30)
            weather.draw(screen)


if __name__ == "__main__":
    unittest.main()
