import unittest

import pygame

from boss import Boss
from collision import resolve_player_boss_collision
from player import Player


class GameplayTests(unittest.TestCase):
    def setUp(self):
        self.keys = {
            pygame.K_a: False,
            pygame.K_LEFT: False,
            pygame.K_d: False,
            pygame.K_RIGHT: False,
        }

    def press_jump(self, player):
        player.handle_event(
            pygame.event.Event(
                pygame.KEYDOWN,
                key=pygame.K_SPACE
            )
        )

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

        player.take_damage(knockback_direction=-1)
        player.update(player.damage_cooldown_duration, self.keys, 800, 600)

        velocity_after_immunity = player.velocity_x
        player.update(0.1, self.keys, 800, 600)

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

    def test_normal_jump_consumes_one_jump(self):
        player = Player(100, 540)
        player.grounded = True
        player.jumps_remaining = player.max_jumps
        self.press_jump(player)

        player.update(0.01, self.keys, 800, 600)

        self.assertEqual(player.jumps_remaining, 1)
        self.assertLess(player.velocity_y, 0)

    def test_airborne_second_jump_resets_vertical_velocity(self):
        player = Player(100, 400)
        player.grounded = True
        player.jumps_remaining = player.max_jumps
        self.press_jump(player)
        player.update(0.01, self.keys, 800, 600)

        player.velocity_y = 250
        self.press_jump(player)
        player.update(0.01, self.keys, 800, 600)

        self.assertEqual(player.jumps_remaining, 0)
        self.assertLess(player.velocity_y, 0)

    def test_third_jump_is_prevented(self):
        player = Player(100, 400)
        player.grounded = True
        player.jumps_remaining = player.max_jumps

        self.press_jump(player)
        player.update(0.01, self.keys, 800, 600)
        self.press_jump(player)
        player.update(0.01, self.keys, 800, 600)

        velocity_before_third_press = player.velocity_y
        self.press_jump(player)
        player.update(0.01, self.keys, 800, 600)

        self.assertEqual(player.jumps_remaining, 0)
        self.assertGreater(player.velocity_y, velocity_before_third_press)

    def test_holding_jump_key_does_not_repeat_jump(self):
        player = Player(100, 400)
        player.grounded = True
        player.jumps_remaining = player.max_jumps
        self.press_jump(player)

        player.update(0.01, self.keys, 800, 600)
        velocity_after_first_jump = player.velocity_y
        player.update(0.01, self.keys, 800, 600)

        self.assertEqual(player.jumps_remaining, 1)
        self.assertGreater(player.velocity_y, velocity_after_first_jump)

    def test_landing_resets_available_jumps(self):
        player = Player(100, 590)
        player.jumps_remaining = 0
        player.velocity_y = 100

        player.update(0.01, self.keys, 800, 600)

        self.assertTrue(player.grounded)
        self.assertEqual(player.jumps_remaining, player.max_jumps)

    def test_coyote_jump_consumes_first_jump(self):
        player = Player(100, 400)
        player.grounded = False
        player.coyote_time = player.coyote_duration
        player.jumps_remaining = player.max_jumps
        self.press_jump(player)

        player.update(0.01, self.keys, 800, 600)

        self.assertEqual(player.jumps_remaining, 1)
        self.assertEqual(player.coyote_time, 0)

    def test_jump_buffer_triggers_after_landing(self):
        player = Player(100, 550)
        player.grounded = False
        player.jumps_remaining = 0
        player.velocity_y = 100
        self.press_jump(player)

        player.update(0.01, self.keys, 800, 600)
        player.update(0.01, self.keys, 800, 600)

        self.assertEqual(player.jumps_remaining, 1)
        self.assertLess(player.velocity_y, 0)

    def test_jump_works_during_dash_and_after_knockback(self):
        player = Player(100, 400)
        player.grounded = True
        player.jumps_remaining = player.max_jumps
        player.dash_timer = player.dash_duration
        player.take_damage(knockback_direction=-1)
        player.grounded = True
        player.jumps_remaining = player.max_jumps
        self.press_jump(player)

        player.update(0.01, self.keys, 800, 600)

        self.assertEqual(player.jumps_remaining, 1)
        self.assertLess(player.velocity_y, 0)


if __name__ == "__main__":
    unittest.main()
