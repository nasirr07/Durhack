
import pygame


def resolve_player_collisions(player, screen_width, floor_y):
    # Horizontal screen boundaries
    if player.x < 0:
        player.x = 0
        player.velocity_x = 0

    if player.x + player.width > screen_width:
        player.x = screen_width - player.width
        player.velocity_x = 0

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
    else:
        player.grounded = False

    # Ceiling collision
    if player.y < 0:
        player.y = 0
        player.velocity_y = 0


def check_collision(rect_a, rect_b):
    """Check whether two rectangular hitboxes overlap."""
    return rect_a.colliderect(rect_b)


def resolve_player_boss_collision(player, boss):
    player_rect = player.rect
    boss_rect = boss.rect

    if not player_rect.colliderect(boss_rect):
        return

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

        player.velocity_x = 0

    else:

        # Player is above the boss
        if player_rect.centery < boss_rect.centery:
            player.y -= overlap_y
            player.velocity_y = 0
            player.grounded = True

        # Player is below the boss
        else:
            player.y += overlap_y
            player.velocity_y = 0