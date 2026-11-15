
import pygame


def resolve_player_collisions(player, screen_width, floor_y):
    # Horizontal screen boundaries
    if player.x < 0:
        player.x = 0
        if player.velocity_x < 0:
            player.velocity_x = 0
        if player.knockback_velocity_x < 0:
            player.knockback_velocity_x = 0

    if player.x + player.width > screen_width:
        player.x = screen_width - player.width
        if player.velocity_x > 0:
            player.velocity_x = 0
        if player.knockback_velocity_x > 0:
            player.knockback_velocity_x = 0

    # Vertical collision with floor
    previous_bottom = player.y + player.height

    # Check whether the player has reached the floor
    if (
        player.velocity_y >= 0
        and previous_bottom >= floor_y
    ):
        player.y = floor_y - player.height
        player.velocity_y = 0
        player.grounded = True
        player.jumps_remaining = player.max_jumps
    else:
        player.grounded = False

    # Ceiling collision
    if player.y < 0:
        player.y = 0
        player.velocity_y = 0


def check_collision(rect_a, rect_b):
    """Check whether two rectangular hitboxes overlap."""
    return rect_a.colliderect(rect_b)


def check_mask_collision(rect_a, mask_a, rect_b, mask_b):
    """Check pixel-accurate overlap between two masks positioned at rect_a and rect_b."""
    if rect_a is None or rect_b is None or mask_a is None or mask_b is None:
        return False
    if not rect_a.colliderect(rect_b):
        return False
    offset = (rect_b.x - rect_a.x, rect_b.y - rect_a.y)
    return mask_a.overlap(mask_b, offset) is not None


def resolve_player_boss_collision(
    player,
    boss,
    screen_width=None,
    floor_y=None
):
    player_rect = player.rect
    boss_rect = boss.rect

    if not player_rect.colliderect(boss_rect):
        player.boss_contact_active = False
        player.boss_collision_started = False
        return False

    player_mask = getattr(player, "body_mask", None)
    boss_mask = getattr(boss, "body_mask", None)
    if player_mask is not None and boss_mask is not None:
        if not check_mask_collision(player_rect, player_mask, boss_rect, boss_mask):
            player.boss_contact_active = False
            player.boss_collision_started = False
            return False

    player.boss_collision_started = not player.boss_contact_active
    player.boss_contact_active = True
    player.boss_collision_direction = (
        -1 if player_rect.centerx < boss_rect.centerx else 1
    )

    # Calculate overlap on both axes
    overlap_x = min(
        player_rect.right - boss_rect.left,
        boss_rect.right - player_rect.left
    )

    overlap_y = min(
        player_rect.bottom - boss_rect.top,
        boss_rect.bottom - player_rect.top
    )

    # Resolve collision on the axis with the smallest overlap
    if overlap_x < overlap_y:

        # Player is to the left of the boss
        if player_rect.centerx < boss_rect.centerx:
            player.x -= overlap_x
        else:
            player.x += overlap_x

    else:

        # Player is above the boss
        if player_rect.centery < boss_rect.centery:
            player.y -= overlap_y
            player.velocity_y = 0
            player.grounded = True
            player.jumps_remaining = player.max_jumps

        # Player is below the boss
        else:
            player.y += overlap_y
            player.velocity_y = 0

    if screen_width is not None and floor_y is not None:
        resolve_player_collisions(player, screen_width, floor_y)

    return True