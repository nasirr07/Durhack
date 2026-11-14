import unittest

import pygame

from boss import Boss
from collision import resolve_player_boss_collision
from player import Player


class GameplayTests(unittest.TestCase):
    def test_player_takes_one_damage_per_contact_cooldown(self):
        player = Player(0, 0)

        player.take_damage()
        player.take_damage()

        self.assertEqual(player.health, player.max_health - 1)

    def test_boss_collision_stays_inside_screen_boundaries(self):
        player = Player(0, 100)
        boss = Boss(20, 100)

        collided = resolve_player_boss_collision(
            player,
            boss,
            screen_width=800,
            floor_y=600
        )

        self.assertTrue(collided)
        self.assertGreaterEqual(player.x, 0)

    def test_damage_starts_flash_and_knocks_player_back(self):
        player = Player(100, 100)

        player.take_damage(knockback_direction=-1)

        self.assertLess(player.velocity_x, 0)
        self.assertLess(player.velocity_y, 0)
        self.assertEqual(
            player.damage_flash_timer,
            player.damage_cooldown_duration
        )

    def test_damage_knockback_persists_during_immunity(self):
        player = Player(100, 100)
        keys = {
            pygame.K_a: False,
            pygame.K_LEFT: False,
            pygame.K_d: False,
            pygame.K_RIGHT: False,
        }

        player.take_damage(knockback_direction=-1)
        player.update(0.1, keys, 800, 600)

        self.assertLess(player.x, 100)

    def test_knockback_decays_after_immunity_ends(self):
        player = Player(100, 100)
        keys = {
            pygame.K_a: False,
            pygame.K_LEFT: False,
            pygame.K_d: False,
            pygame.K_RIGHT: False,
        }

        player.take_damage(knockback_direction=-1)
        player.update(player.damage_cooldown_duration, keys, 800, 600)

        velocity_after_immunity = player.velocity_x
        player.update(0.1, keys, 800, 600)

        self.assertLess(velocity_after_immunity, 0)
        self.assertLess(player.velocity_x, 0)
        self.assertGreater(player.velocity_x, velocity_after_immunity)

    def test_boss_contact_triggers_damage_once_until_separation(self):
        player = Player(100, 100)
        boss = Boss(120, 100)

        first_collision = resolve_player_boss_collision(
            player,
            boss,
            screen_width=800,
            floor_y=600
        )
        if player.boss_collision_started:
            player.take_damage(
                knockback_direction=player.boss_collision_direction
            )
        health_after_first_collision = player.health

        player.x = 100
        second_collision = resolve_player_boss_collision(
            player,
            boss,
            screen_width=800,
            floor_y=600
        )
        if player.boss_collision_started:
            player.take_damage(
                knockback_direction=player.boss_collision_direction
            )

        self.assertTrue(first_collision)
        self.assertTrue(second_collision)
        self.assertEqual(player.health, health_after_first_collision)

    def test_boss_collision_direction_matches_player_side(self):
        player = Player(100, 100)
        boss = Boss(120, 100)

        resolve_player_boss_collision(player, boss)

        self.assertEqual(player.boss_collision_direction, -1)


if __name__ == "__main__":
    unittest.main()
