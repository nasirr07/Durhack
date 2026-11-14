import os
import pygame

# Each Samurai sprite's standing body occupies a 16x14 base box (body_x, body_y, 16, 14).
# Attack/death sheets use larger cells around that 16x14 body box for sword swings.
# Storing ((cell_w, cell_h), (body_x, body_y), (pad_x, pad_y)) lets us scale every
# sheet by the exact same pixel ratio (target_w / 16, target_h / 14) so the character
# is identical in size across idle, run, jump, and attacks.
_BASE_BODY_W = 16
_BASE_BODY_H = 14

_SHEET_SPECS = {
    "idle_spritesheet": ((16, 16), (0, 0), (0, 0)),
    "run_spritesheet": ((16, 16), (0, 0), (0, 0)),
    "jump_spritesheet": ((16, 16), (0, 2), (0, 0)),
    "hit_spritesheet": ((16, 16), (0, 2), (0, 0)),
    "healing_spritesheet": ((16, 32), (0, 4), (0, 0)),
    "death_spritesheet": ((32, 16), (0, 2), (4, 0)),
    "attack_spritesheet": ((48, 48), (13, 18), (15, 3)),
    "attack_down_spritesheet": ((48, 32), (15, 0), (12, 7)),
    "dash_attack_spritesheet": ((48, 32), (13, 2), (13, 2)),
    "attack_up_spritesheet": ((64, 64), (24, 34), (10, 6)),
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
        """Slice a spritesheet into a list of frame Surfaces where the character body is (width x height)."""
        target_w = width or self.default_width
        target_h = height or self.default_height

        if isinstance(sheet, str) and name is None:
            name = os.path.splitext(os.path.basename(sheet))[0]

        sheet_surface = self._ensure_surface(sheet)
        sheet_w, sheet_h = sheet_surface.get_size()

        if name in _SHEET_SPECS:
            (cell_w, cell_h), (bx, by), (pad_x, pad_y) = _SHEET_SPECS[name]
            crop_w = _BASE_BODY_W + 2 * pad_x
            crop_h = _BASE_BODY_H + 2 * pad_y
            out_w = round(crop_w * (target_w / _BASE_BODY_W))
            out_h = round(crop_h * (target_h / _BASE_BODY_H))
        else:
            bx = by = pad_x = pad_y = 0
            if name == "double_jump_spritesheet":
                cell_w, cell_h = 32, 32
            elif name == "tiles_spritesheet":
                cell_w, cell_h = 24, 24
            elif sheet_w >= target_w and sheet_h >= target_h:
                cell_w, cell_h = target_w, target_h
            else:
                cell_w, cell_h = sheet_w, sheet_h
            crop_w, crop_h = cell_w, cell_h
            out_w, out_h = target_w, target_h

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

                if name in _SHEET_SPECS:
                    # Blit onto a symmetrically padded surface centered on the 16x14 character body
                    frame_surf = pygame.Surface((crop_w, crop_h), pygame.SRCALPHA)
                    frame_surf.blit(cell_surf, (pad_x - bx, pad_y - by))
                else:
                    frame_surf = cell_surf

                if frame_surf.get_size() != (out_w, out_h):
                    frame_surf = pygame.transform.scale(frame_surf, (out_w, out_h))

                if pygame.display.get_surface():
                    frame_surf = frame_surf.convert_alpha()

                frames.append(frame_surf)

        if not frames:
            frames.append(self.get_image(sheet_surface, 0, target_w, target_h, colour=colour))

        return frames

    # PascalCase aliases for backwards compatibility
    GetImage = get_image
    GetSprites = get_sprites
