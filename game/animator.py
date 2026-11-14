import pygame


class Animator:
    ASSETS = {}

    def __init__(self, entity_group="Samurai", default_state="idle", fps=10, animation_speed=1.0):
        self.entity_group = entity_group
        self.current_state = default_state
        self.fps = fps
        self.animation_speed = animation_speed
        self.frame_index = 0.0
        self.loop = True
        self.finished = False
        self.flip_x = False

    def get_frames(self, state=None):
        """Find and return the list of frame Surfaces for a given animation state."""
        target = state or self.current_state
        if not self.ASSETS:
            return []

        # Allow slash-separated paths like "Samurai/Attack/attack"
        if isinstance(target, str) and "/" in target:
            node = self.ASSETS
            for part in target.split("/"):
                if isinstance(node, dict) and part in node:
                    node = node[part]
                else:
                    return []
            return node if isinstance(node, list) else [node]

        # Check under entity_group (e.g. ASSETS["Samurai"][target] or ASSETS["Samurai"]["Attack"][target])
        group_dict = self.ASSETS.get(self.entity_group, {})
        if isinstance(group_dict, dict):
            if target in group_dict and isinstance(group_dict[target], list):
                return group_dict[target]
            for sub in group_dict.values():
                if isinstance(sub, dict) and target in sub and isinstance(sub[target], list):
                    return sub[target]

        # Fallback: top-level ASSETS key
        if target in self.ASSETS:
            val = self.ASSETS[target]
            return val if isinstance(val, list) else [val]

        return []

    def get_asset(self, *keys):
        """Retrieve any nested asset or dict from ASSETS by keys."""
        node = self.ASSETS
        for key in keys:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return None
        return node

    def set_state(self, state, loop=True, reset=False):
        """Switch animation state; resets to frame 0 only when the state changes (or reset=True)."""
        if state != self.current_state or reset:
            self.current_state = state
            self.frame_index = 0.0
            self.finished = False
        self.loop = loop

    def update_from_player(self, player):
        """Automatically pick the Samurai animation state and facing direction from a Player instance."""
        self.flip_x = player.facing < 0

        if player.health <= 0:
            self.set_state("death", loop=False)
        elif player.damage_flash_timer > 0:
            self.set_state("hit", loop=True)
        elif player.dash_timer > 0:
            self.set_state("dash_attack", loop=False)
        elif player.attack_timer > 0:
            self.set_state("attack", loop=False)
        elif not player.grounded:
            self.set_state("jump", loop=False)
        elif abs(player.velocity_x) > 1.0:
            self.set_state("run", loop=True)
        else:
            self.set_state("idle", loop=True)

    def update(self, dt=1 / 60, player=None):
        """Advance the animation timer by dt seconds."""
        if player is not None:
            self.update_from_player(player)

        frames = self.get_frames()
        if not frames:
            return None

        self.frame_index += dt * self.fps * self.animation_speed

        if self.loop:
            self.frame_index %= len(frames)
        else:
            if self.frame_index >= len(frames) - 1:
                self.frame_index = float(len(frames) - 1)
                self.finished = True

        return self.get_current_frame()

    def get_current_frame(self, flip_x=None):
        """Return the current animation frame Surface (flipped if facing left)."""
        frames = self.get_frames()
        if not frames:
            return None

        idx = int(self.frame_index) % len(frames)
        frame = frames[idx]

        should_flip = self.flip_x if flip_x is None else flip_x
        if should_flip:
            return pygame.transform.flip(frame, True, False)
        return frame

    def draw(self, screen, pos_or_rect, flip_x=None):
        """Draw the current frame onto screen at the given (x, y) or pygame.Rect."""
        frame = self.get_current_frame(flip_x=flip_x)
        if frame is not None:
            screen.blit(frame, pos_or_rect)

    # PascalCase aliases
    GetFrames = get_frames
    GetAsset = get_asset
    SetState = set_state
    Update = update
    GetCurrentFrame = get_current_frame
    Draw = draw
