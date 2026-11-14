import os
import pygame

# Native grid cell dimensions (cell_w, cell_h) and optional active crop (x, y, w, h)
# inside each cell so the Samurai stays consistent in size and floor-aligned when scaled to 60x60.
_SHEET_SPECS = {
    "idle_spritesheet": ((16, 16), (0, 0, 16, 14)),
    "run_spritesheet": ((16, 16), (0, 0, 16, 14)),
    "jump_spritesheet": ((16, 16), (0, 0, 16, 16)),
    "hit_spritesheet": ((16, 16), (0, 0, 16, 16)),
    "healing_spritesheet": ((16, 32), (0, 4, 16, 16)),
    "double_jump_spritesheet": ((32, 32), (0, 0, 32, 32)),
    "death_spritesheet": ((32, 16), (0, 0, 20, 16)),
    "attack_spritesheet": ((48, 48), (6, 12, 36, 22)),
    "attack_down_spritesheet": ((48, 32), (12, 0, 28, 21)),
    "dash_attack_spritesheet": ((48, 32), (8, 2, 32, 16)),
    "attack_up_spritesheet": ((64, 64), (18, 28, 26, 20)),
    "tiles_spritesheet": ((24, 24), (0, 0, 24, 24)),
}


class SpriteSheet:
    def __init__(self, default_width=60, default_height=60):
        self.default_width = default_width
        self.default_height = default_height

    def _ensure_surface(self, sheet):
        if isinstance(sheet, str):
            loaded = pygame.image.load(sheet)
            return loaded.convert_alpha() if pygame.display.get_surface() else loaded
        return sheet

    def get_image(self, sheet, frame=0, width=None, height=None, scale=1, colour=None, row=0):
        """Extract a single frame from a spritesheet surface (or file path)."""
        sheet_surface = self._ensure_surface(sheet)
        w = width or self.default_width
        h = height or self.default_height

        img = pygame.Surface((w, h), pygame.SRCALPHA)
        img.blit(sheet_surface, (0, 0), (frame * w, row * h, w, h))

        if scale != 1:
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))

        if colour is not None:
            img.set_colorkey(colour)

        return img.convert_alpha() if pygame.display.get_surface() else img

    def get_sprites(self, sheet, width=None, height=None, colour=None, name=None):
        """Slice a spritesheet into a list of (width x height) frame Surfaces (default 60x60)."""
        target_w = width or self.default_width
        target_h = height or self.default_height

        if isinstance(sheet, str) and name is None:
            name = os.path.splitext(os.path.basename(sheet))[0]

        sheet_surface = self._ensure_surface(sheet)
        sheet_w, sheet_h = sheet_surface.get_size()

        crop_rect = None
        if name in _SHEET_SPECS:
            (cell_w, cell_h), crop_rect = _SHEET_SPECS[name]
        elif sheet_w >= target_w and sheet_h >= target_h:
            cell_w, cell_h = target_w, target_h
        else:
            cell_w, cell_h = sheet_w, sheet_h

        cols = max(1, sheet_w // cell_w)
        rows = max(1, sheet_h // cell_h)

        frames = []
        for r in range(rows):
            for c in range(cols):
                cell_surf = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                cell_surf.blit(sheet_surface, (0, 0), (c * cell_w, r * cell_h, cell_w, cell_h))

                if colour is not None:
                    cell_surf.set_colorkey(colour)
                elif name == "double_jump_spritesheet":
                    cell_surf.set_colorkey((0, 0, 0))

                # Skip empty padding cells in multi-row grids
                if pygame.mask.from_surface(cell_surf).count() == 0:
                    continue

                if crop_rect is not None:
                    cx, cy, cw, ch = crop_rect
                    cropped = pygame.Surface((cw, ch), pygame.SRCALPHA)
                    cropped.blit(cell_surf, (0, 0), (cx, cy, cw, ch))
                    frame_surf = cropped
                else:
                    frame_surf = cell_surf

                if frame_surf.get_size() != (target_w, target_h):
                    frame_surf = pygame.transform.scale(frame_surf, (target_w, target_h))

                if pygame.display.get_surface():
                    frame_surf = frame_surf.convert_alpha()

                frames.append(frame_surf)

        if not frames:
            frames.append(self.get_image(sheet_surface, 0, target_w, target_h, colour=colour))

        return frames

    # PascalCase aliases for backwards compatibility
    GetImage = get_image
    GetSprites = get_sprites
