
from collision import check_collision

class CombatSystem:
    def __init__(self):
        self.active_attacks = []
        self.last_hit_attack_id = -1

    def update(self, player, boss):
        attack_rect = player.attack_rect

        if attack_rect is None:
            return

        # Check whether this swing has already damaged the boss
        if player.attack_id == self.last_hit_attack_id:
            return

        # Check collision and apply damage
        if check_collision(attack_rect, boss.rect):
            boss.take_damage(player.attack_damage)
            player.attack_hit = True
            self.last_hit_attack_id = player.attack_id