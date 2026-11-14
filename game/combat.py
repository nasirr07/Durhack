
from collision import check_collision


class CombatSystem:
    def __init__(self):
        self.active_attacks = []

    def damage_boss(self, attack_rect, damage, boss):
        """
        Check whether an attack hits the boss.
        Apply damage if a collision occurs.

        Returns True if the attack hits.
        """
        if check_collision(attack_rect, boss.rect):
            boss.take_damage(damage)
            return True

        return False
