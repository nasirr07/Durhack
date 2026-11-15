from collision import check_collision, check_mask_collision


class CombatSystem:
    def __init__(self):
        self.active_attacks = []
        self.last_hit_attack_id = -1

    def update(self, player, boss):
        # 1. Check boss's mask-based cleaver attack hitting the player
        if hasattr(boss, "check_attack_hit") and boss.check_attack_hit(player):
            player.take_damage(
                damage=getattr(boss, "attack_damage", 1),
                knockback_direction=getattr(boss, "facing", -1),
            )

        # 2. Check player's attack hitting the boss
        attack_rect = player.attack_rect
        if attack_rect is None:
            return

        # Check whether this swing has already damaged the boss
        if player.attack_id == self.last_hit_attack_id:
            return

        attack_mask = getattr(player, "attack_mask", None)
        boss_mask = getattr(boss, "body_mask", None)

        if attack_mask is not None and boss_mask is not None:
            hit = check_mask_collision(attack_rect, attack_mask, boss.rect, boss_mask)
        else:
            hit = check_collision(attack_rect, boss.rect)

        if hit:
            boss.take_damage(player.attack_damage)
            self.last_hit_attack_id = player.attack_id
