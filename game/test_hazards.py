import unittest

import pygame

from hazards import EarthquakeHazard, HazardPhase, TiltDetector
from player import Player


class TiltDetectorTests(unittest.TestCase):
    def test_repeated_direction_readings_do_not_count(self):
        detector = TiltDetector()
        for timestamp in (0.0, 0.1, 0.2, 0.3, 0.4):
            self.assertFalse(detector.sample("left", timestamp))

    def test_four_alternating_changes_trigger_inside_window(self):
        detector = TiltDetector()
        self.assertFalse(detector.sample("left", 0.0))
        self.assertFalse(detector.sample("right", 0.2))
        self.assertFalse(detector.sample("left", 0.4))
        self.assertFalse(detector.sample("right", 0.6))
        self.assertTrue(detector.sample("left", 0.8))

    def test_neutral_readings_are_ignored_and_old_changes_expire(self):
        detector = TiltDetector()
        detector.sample("left", 0.0)
        detector.sample("right", 0.2)
        detector.sample("none", 0.3)
        detector.sample("left", 0.4)
        self.assertFalse(detector.sample("right", 2.3))


class EarthquakeHazardTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.hazard = EarthquakeHazard(800, 600, seed=1)
        self.player = Player(300, 540)

    def tearDown(self):
        pygame.quit()

    def trigger(self):
        for direction in ("left", "right", "left", "right", "left"):
            self.hazard.update(0.2, direction, self.player)

    def test_warning_then_boulder_then_cooldown_phases(self):
        self.trigger()
        self.assertEqual(self.hazard.phase, HazardPhase.WARNING)
        self.assertNotEqual(self.hazard.shake_offset, (0, 0))
        self.hazard.update(1.5, "right", self.player)
        self.assertEqual(self.hazard.phase, HazardPhase.BOULDERS)
        self.assertEqual(self.hazard.shake_offset, (0, 0))
        self.hazard.boulders[0].speed = 0
        self.hazard.update(5.0, "left", self.player)
        self.assertEqual(self.hazard.phase, HazardPhase.COOLDOWN)
        self.assertEqual(len(self.hazard.boulders), 1)
        self.hazard.update(0.8, "right", self.player)
        self.assertEqual(len(self.hazard.boulders), 1)

    def test_boulders_are_capped_and_removed_at_ground(self):
        self.trigger()
        self.hazard.update(1.5, "none", self.player)
        self.hazard.update(0.0, "none", self.player)
        self.assertLessEqual(len(self.hazard.boulders), 3)
        self.hazard.boulders[0].y = 580
        self.hazard.update(0.1, "none", self.player)
        self.assertLessEqual(len(self.hazard.boulders), 2)

    def test_boulder_damages_player_once(self):
        self.trigger()
        self.hazard.update(1.5, "none", self.player)
        boulder = self.hazard.boulders[0]
        boulder.x = self.player.x
        boulder.y = self.player.y
        health_before = self.player.health
        self.hazard.update(0.0, "none", self.player)
        self.hazard.update(0.0, "none", self.player)
        self.assertEqual(self.player.health, health_before - 1)
        self.assertTrue(boulder.hit_player)

    def test_direction_is_ignored_while_active_and_cooldown(self):
        self.trigger()
        self.assertEqual(self.hazard.phase, HazardPhase.WARNING)
        for direction in ("right", "left", "right", "left", "right", "left", "right", "left"):
            self.hazard.update(0.2, direction, self.player)
        self.assertNotEqual(self.hazard.phase, HazardPhase.WARNING)
        self.assertNotEqual(self.hazard.phase, HazardPhase.IDLE)


if __name__ == "__main__":
    unittest.main()
