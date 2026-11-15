import os

import pygame


PALETTE = {
    "ink": (20, 18, 28),
    "panel": (27, 24, 38),
    "panel_light": (53, 45, 64),
    "cream": (239, 224, 172),
    "muted": (174, 166, 151),
    "wind": (129, 199, 183),
    "ember": (219, 111, 91),
    "shadow": (8, 8, 13),
}


class PixelUI:
    def __init__(self, screen_size, assets_dir):
        self.width, self.height = screen_size
        fonts_dir = os.path.join(assets_dir, "Fonts")
        scale = max(1, min(self.width, self.height) // 720)

        self.title_font = pygame.font.Font(
            os.path.join(fonts_dir, "PressStart2P-Regular.ttf"),
            40 * scale,
        )
        self.heading_font = pygame.font.Font(
            os.path.join(fonts_dir, "PressStart2P-Regular.ttf"),
            16 * scale,
        )
        self.body_font = pygame.font.Font(
            os.path.join(fonts_dir, "Silkscreen-Regular.ttf"),
            18 * scale,
        )
        self.small_font = pygame.font.Font(
            os.path.join(fonts_dir, "Silkscreen-Regular.ttf"),
            13 * scale,
        )
        self.scale = scale

    def draw_start(self, screen, background_surface, floor_surface, selected_index):
        self._draw_arena(screen, background_surface, floor_surface)
        self._draw_overlay(screen)

        title = self.title_font.render("MICROROGUE", False, PALETTE["cream"])
        shadow = self.title_font.render("MICROROGUE", False, PALETTE["shadow"])
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        screen.blit(shadow, title_rect.move(4 * self.scale, 4 * self.scale))
        screen.blit(title, title_rect)

        subtitle = self.body_font.render(
            "A blade, a boss, and the wind between them.",
            False,
            PALETTE["muted"],
        )
        screen.blit(subtitle, subtitle.get_rect(center=(self.width // 2, title_rect.bottom + 38 * self.scale)))

        buttons = self._button_rects(title_rect.bottom + 150 * self.scale)
        self._draw_button(screen, buttons[0], "Start game", selected_index == 0)
        self._draw_button(screen, buttons[1], "Quit", selected_index == 1)
        self._draw_hint(screen, "Up / Down  select     Enter  confirm")
        return buttons

    def draw_end(
        self,
        screen,
        background_surface,
        floor_surface,
        session,
        victory,
        selected_index,
    ):
        self._draw_arena(screen, background_surface, floor_surface)
        session.player.draw(screen)
        session.boss.draw(screen)
        self._draw_overlay(screen, opacity=185)

        colour = PALETTE["wind"] if victory else PALETTE["ember"]
        heading = "VICTORY" if victory else "DEFEAT"
        message = "The boss falls. The arena is yours." if victory else "The arena claims another challenger."

        title = self.heading_font.render(heading, False, colour)
        screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 3)))

        body = self.body_font.render(message, False, PALETTE["cream"])
        screen.blit(body, body.get_rect(center=(self.width // 2, self.height // 3 + 52 * self.scale)))

        buttons = self._button_rects(self.height // 2 + 55 * self.scale)
        self._draw_button(screen, buttons[0], "Restart", selected_index == 0)
        self._draw_button(screen, buttons[1], "Return to menu", selected_index == 1)
        self._draw_hint(screen, "Up / Down  select     Enter  confirm")
        return buttons

    def _draw_arena(self, screen, background_surface, floor_surface):
        screen.blit(background_surface, (0, 0))
        screen.blit(floor_surface, (0, self.height - floor_surface.get_height()))

    def _draw_overlay(self, screen, opacity=215):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((*PALETTE["ink"], opacity))
        screen.blit(overlay, (0, 0))

    def _draw_button(self, screen, rect, label, selected):
        fill = PALETTE["panel_light"] if selected else PALETTE["panel"]
        outline = PALETTE["cream"] if selected else PALETTE["muted"]
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, outline, rect, max(1, self.scale))
        if selected:
            marker = self.small_font.render(">", False, PALETTE["wind"])
            screen.blit(marker, self._selection_marker_rect(rect))
        text = self.body_font.render(label, False, PALETTE["cream"])
        screen.blit(text, self._button_text_rect(rect, label))

    def _button_rects(self, top):
        width = min(360 * self.scale, self.width - 64 * self.scale)
        height = 34 * self.scale
        gap = 16 * self.scale
        left = (self.width - width) // 2
        return (
            pygame.Rect(left, top, width, height),
            pygame.Rect(left, top + height + gap, width, height),
        )

    def _selection_marker_rect(self, button_rect):
        marker = self.small_font.render(">", False, PALETTE["wind"])
        return marker.get_rect(
            midleft=(
                button_rect.left - 8 * self.scale,
                button_rect.centery,
            )
        )

    def _button_text_rect(self, button_rect, label):
        text = self.body_font.render(label, False, PALETTE["cream"])
        return text.get_rect(center=button_rect.center)

    def _draw_hint(self, screen, text):
        hint = self.small_font.render(text, False, PALETTE["muted"])
        screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height - 28 * self.scale)))
