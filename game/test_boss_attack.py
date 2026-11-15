import unittest

import pygame

from boss import Boss, BossAttackPhase
from collision import resolve_boss_attack
from player import Player


def fake_animations():
    animations = {}
    for row, count in (
        ("row_1", 6),
        ("row_2", 12),
        ("row_3", 15),
        ("row_4", 5),
        ("row_5", 22),
    ):
        frames = []
        for _ in range(count):
            frame = pygame.Surface((288, 160), pygame.SRCALPHA)
            pygame.draw.rect(frame, (255, 255, 255), (40, 20, 200, 140))
            frames.append(frame)
        animations[row] = frames
    return animations


class BossAttackTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))
        self.arena = pygame.Rect(0, 0, 800, 600)
        self.boss = Boss(self.arena, animations=fake_animations())
        self.player = Player(200, 300)

    def tearDown(self):
        pygame.quit()

    def test_boss_is_grounded_at_the_right_edge_and_faces_left(self):
        self.assertEqual(self.boss.facing, -1)
        self.assertEqual(self.boss.visual_rect.right, self.arena.right - Boss.RIGHT_MARGIN)
        self.assertEqual(self.boss.visual_rect.bottom, self.arena.bottom)

    def test_boss_does_not_change_horizontal_position(self):
        initial_x = self.boss.visual_rect.x
        self.boss.update(3.0, self.arena.bottom, self.player)
        self.assertEqual(self.boss.visual_rect.x, initial_x)

    def test_attack_starts_after_five_seconds(self):
        self.boss.update(Boss.ATTACK_INTERVAL - 0.01, self.arena.bottom, self.player)
        self.assertEqual(self.boss.attack_phase, BossAttackPhase.IDLE)

        self.boss.update(0.01, self.arena.bottom, self.player)
        self.assertEqual(self.boss.attack_phase, BossAttackPhase.WINDUP)
        self.assertEqual(self.boss.current_animation, "row_3")
        self.assertEqual(self.boss.animation_index, 0)

    def test_attack_returns_to_idle_after_row_three_finishes(self):
        self.boss.update(Boss.ATTACK_INTERVAL, self.arena.bottom, self.player)
        self.boss.update(Boss.ATTACK_DURATION, self.arena.bottom, self.player)
        self.assertEqual(self.boss.attack_phase, BossAttackPhase.IDLE)
        self.assertEqual(self.boss.current_animation, "row_1")

    def test_attack_hitbox_is_left_of_boss_only_during_active_phase(self):
        self.boss.update(Boss.ATTACK_INTERVAL, self.arena.bottom, self.player)
        self.boss.update(Boss.ACTIVE_START, self.arena.bottom, self.player)
        attack_rect = self.boss.attack_rect

        self.assertIsNotNone(attack_rect)
        self.assertLessEqual(attack_rect.right, self.boss.rect.left)

        self.boss.update(
            Boss.ACTIVE_END - Boss.ACTIVE_START,
            self.arena.bottom,
            self.player,
        )
        self.assertIsNone(self.boss.attack_rect)

    def test_attack_damages_player_only_once(self):
        self.boss.update(Boss.ATTACK_INTERVAL, self.arena.bottom, self.player)
        self.boss.update(Boss.ACTIVE_START, self.arena.bottom, self.player)
        attack_rect = self.boss.attack_rect
        self.player.x = attack_rect.centerx
        self.player.y = attack_rect.centery
        health_before = self.player.health

        self.assertTrue(resolve_boss_attack(self.boss, self.player))
        self.assertFalse(resolve_boss_attack(self.boss, self.player))
        self.assertEqual(self.player.health, health_before - 1)

    def test_damage_uses_row_four_and_health_clamps(self):
        self.boss.take_damage(self.boss.max_health + 1)
        self.assertEqual(self.boss.health, 0)
        self.assertEqual(self.boss.current_animation, "row_4")
        self.assertIsNone(self.boss.attack_rect)

    def test_body_hitbox_is_separate_and_anchored_to_visual(self):
        self.assertEqual(self.boss.rect.midbottom, self.boss.visual_rect.midbottom)
        self.assertNotEqual(self.boss.rect.size, self.boss.visual_rect.size)


if __name__ == "__main__":
    unittest.main()
