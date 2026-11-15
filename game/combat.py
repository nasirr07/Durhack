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

        # 2. Check boss's ranged fireballs hitting the player via mask collision
        player_mask = getattr(player, "body_mask", None)
        for fireball in getattr(boss, "fireballs", ()):
            if not fireball.active:
                continue
            if player_mask is not None and getattr(fireball, "mask", None) is not None:
                hit_fb = check_mask_collision(
                    fireball.rect, fireball.mask, player.rect, player_mask
                )
            else:
                hit_fb = check_collision(fireball.rect, player.rect)

            if hit_fb:
                fireball.active = False
                knockback_dir = -1 if fireball.vx < 0 else 1
                player.take_damage(
                    damage=getattr(fireball, "damage", 1),
                    knockback_direction=knockback_dir,
                )

        # 3. Check boss's sky-drop heat waves (player is safe inside the gap)
        for hw in getattr(boss, "heat_waves", ()):
            if hw.check_hit(player):
                knockback_dir = -1 if player.rect.centerx < hw.gap_rect.centerx else 1
                player.take_damage(
                    damage=getattr(hw, "damage", 1),
                    knockback_direction=knockback_dir,
                )

        # 4. Check boss's incantation laser beam hitting the player
        for laser in getattr(boss, "lasers", ()):
            if laser.check_hit(player):
                player.take_damage(
                    damage=getattr(laser, "damage", 1),
                    knockback_direction=getattr(laser, "facing", -1),
                )

        # 5. Check player's attack hitting the boss
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
            player.attack_hit = True
            if player.audio is not None:
                player.audio.play("player_attack_hit")
            self.last_hit_attack_id = player.attack_id
