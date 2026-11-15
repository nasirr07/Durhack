import unittest

import pygame

from boss import Boss
from collision import resolve_player_boss_collision
from combat import CombatSystem
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

    def test_holding_s_accelerates_airborne_falling(self):
        normal = Player(100, 100)
        fast = Player(100, 100)
        normal.grounded = False
        fast.grounded = False
        normal.velocity_y = 200
        fast.velocity_y = 200

        fast_keys = dict(self.keys)
        fast_keys[pygame.K_s] = True
        normal.update(0.1, self.keys, 800, 600)
        fast.update(0.1, fast_keys, 800, 600)

        self.assertGreater(fast.velocity_y, normal.velocity_y)
        self.assertGreater(fast.y, normal.y)

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

    def test_boss_has_tight_body_hitbox_and_mask(self):
        boss = Boss(300, 100)
        self.assertEqual(boss.rect.size, (boss.width, boss.height))
        self.assertGreater(boss.body_mask.count(), 0)
        # Player standing in the empty transparent margin to the left of the boss does NOT collide with the body
        player = Player(200, 150)
        self.assertFalse(resolve_player_boss_collision(player, boss))

    def test_boss_cleaver_attack_mask_damages_player(self):
        boss = Boss(300, 100)
        player = Player(210, 150)  # In front of boss's left-facing cleaver swing
        combat = CombatSystem()

        boss.start_attack()
        boss.animation_index = 10  # Active cleave frame
        boss._sync_image()

        self.assertTrue(boss.is_attack_active)
        self.assertIsNotNone(boss.attack_rect)
        self.assertIsNotNone(boss.attack_mask)

        combat.update(player, boss)
        self.assertEqual(player.health, player.max_health - 1)

    def test_boss_shoots_fireballs_only_when_temperature_over_26(self):
        boss = Boss(600, 100)
        player = Player(100, 250)
        combat = CombatSystem()

        # At 26 C or below, neither fireballs nor heat waves are spawned
        boss.update(2.5, 600, player=player, temperature=26.0)
        self.assertEqual(len(boss.fireballs), 0)
        self.assertEqual(len(boss.heat_waves), 0)

        # Above 26 C, boss summons a volley of 5 fireballs at once that fade in and linger first
        boss.update(0.85, 600, player=player, temperature=27.0)
        self.assertEqual(len(boss.fireballs), 5)
        self.assertTrue(all(not fb.launched for fb in boss.fireballs))
        self.assertLess(boss.fireballs[0].alpha, 255)

        # After 0.8s, only the first fireball (launch_delay=0.75s) has launched sequentially
        boss.update(0.8, 600, player=player, temperature=27.0)
        launched_states = [fb.launched for fb in boss.fireballs]
        self.assertEqual(launched_states, [True, False, False, False, False])

        # Move first fireball onto player and verify mask hit damages player and despawns fireball
        fb = boss.fireballs[0]
        fb.x = player.x
        fb.y = player.y
        combat.update(player, boss)
        self.assertEqual(player.health, player.max_health - 1)
        self.assertFalse(fb.active)

    def test_heat_wave_drops_from_sky_and_safe_gap_protects_player(self):
        boss = Boss(800, 100)
        combat = CombatSystem()

        hw = boss.spawn_heat_wave(gap_x=200, arena_width=700)
        # Advance past telegraph so the heat wave is actively dropping at y=200
        hw.age = hw.telegraph_duration + 0.1
        hw.y = 200.0

        # Player standing inside the safe gap (x=230, width=60 inside gap 200..360) is completely safe
        safe_player = Player(230, 210)
        combat.update(safe_player, boss)
        self.assertEqual(safe_player.health, safe_player.max_health)

        # Player standing outside the safe gap (x=60, width=60 inside left flame curtain) takes damage
        hit_player = Player(60, 210)
        combat.update(hit_player, boss)
        self.assertEqual(hit_player.health, hit_player.max_health - 1)


if __name__ == "__main__":
    unittest.main()
