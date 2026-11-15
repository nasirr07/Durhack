import os
import random
import threading
import pygame

from ui import PALETTE

try:
    from google import genai
except ImportError:
    genai = None

# You can paste your key here directly, or put GEMINI_API_KEY=... inside d:\Me\Durhack\.env
GEMINI_API_KEY = ""


def _resolve_api_key():
    if GEMINI_API_KEY and GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE":
        return GEMINI_API_KEY.strip()

    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.isfile(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                        val = v.strip().strip("\"'")
                        if val and val != "PASTE_YOUR_GEMINI_API_KEY_HERE":
                            return val
        except OSError:
            pass

    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


SYSTEM_INSTRUCTION = (
    "You are the giant pixel-art boss in MicroRogue, a retro 2D boss-rush game "
    "controlled with BBC micro:bit sensors (temperature, light level, tilt). "
    "Write ONE short, punchy retro RPG / Pokemon-style boss taunt (max 14 words, "
    "no quotes, no emojis, plain ASCII). Reference the live sensor or combat event."
)

FALLBACK_TAUNTS = {
    "intro": [
        "CHALLENGER! STEP INTO MY ARENA AND FACE ANCIENT STEEL!",
        "YOU DARE APPROACH?! EVEN THE WIND BOWS BEFORE MY CLEAVER!",
    ],
    "fire": [
        "THE ROOM HITS {temp}C! DROWN IN MY SCORCHING HEAT WAVE!",
        "{temp} DEGREES?! MY BLAZING FIREBALLS AWAKEN AT YOUR HEAT!",
        "FEEL THE ARENA BOIL AT {temp}C! NO SAFE GAP WILL SAVE YOU!",
    ],
    "dark": [
        "LIGHT LEVEL {light}?! HIDING IN THE SHADOWS WONT SAVE YOU!",
        "THE DARKNESS FALLS AT {light} LIGHT... MY BLADE STILL SEES YOU!",
    ],
    "tilt": [
        "TILTING THE WORLD {dir}?! LET THE EARTHQUAKE SHATTER YOUR FEET!",
        "THE GROUND TREMBLES {dir}! TRY JUMPING NOW, LITTLE WARRIOR!",
    ],
    "laser": [
        "COWARD AT RANGE! MY ORANGE INCANTATION LASER WILL PIERCE YOU!",
        "KEEP RUNNING! MY RUNIC CIRCLE LOCKS ONTO YOUR ALTITUDE!",
    ],
    "boss_low": [
        "IMPOSSIBLE! MY ARMOR CRACKS... NOW WITNESS MY TRUE WRATH!",
        "YOU BLEED ME DOWN TO {boss_hp} HP?! I WILL CLEAVE THIS ARENA!",
    ],
    "player_low": [
        "ONLY {player_hp} HEARTS LEFT! ONE MORE SWING ENDS YOUR RUN!",
        "YOUR STEPS FALTER! KNEEL BEFORE THE ARENA GUARDIAN!",
    ],
}


class BossTauntBox:
    """Pokemon-style bottom dialogue box with Gemini API generation and typewriter blip sound."""

    CHAR_SPEED = 28.0        # characters revealed per second
    HOLD_DURATION = 3.2      # seconds to keep completed text visible
    COOLDOWN_DURATION = 8.5  # minimum seconds between automatic taunts
    BOX_HEIGHT = 96
    MAX_WIDTH = 860
    BOTTOM_MARGIN = 18

    def __init__(self, screen_size, body_font, small_font, audio=None):
        self.width, self.height = screen_size
        self.body_font = body_font
        self.small_font = small_font
        self.audio = audio

        box_w = min(self.MAX_WIDTH, self.width - 96)
        self.rect = pygame.Rect(
            (self.width - box_w) // 2,
            self.height - self.BOTTOM_MARGIN - self.BOX_HEIGHT,
            box_w,
            self.BOX_HEIGHT,
        )

        self._client = None
        api_key = _resolve_api_key()
        if genai is not None and api_key:
            try:
                self._client = genai.Client(api_key=api_key)
            except Exception:
                self._client = None

        self._lock = threading.Lock()
        self._pending_text = None
        self._request_in_flight = False
        self.reset()

    def reset(self):
        with self._lock:
            self._pending_text = None
        self.full_text = ""
        self.visible_chars = 0.0
        self.last_blip_char = 0
        self.hold_timer = 0.0
        self.active = False
        self.cooldown = 0.6
        self._seen_intro = False
        self._was_hot = False
        self._was_dark = False
        self._was_boss_low = False
        self._was_player_low = False

    def trigger_taunt(self, category, context):
        """Queue a Gemini API taunt request in a background thread (with instant fallback support)."""
        if self._request_in_flight:
            return

        fallback = self._format_fallback(category, context)
        if self._client is None:
            self._start_display(fallback)
            return

        self._request_in_flight = True
        prompt = (
            f"Event: {category}. "
            f"Room temperature: {context.get('temp')}C, "
            f"Light sensor: {context.get('light')}/255, "
            f"Tilt direction: {context.get('dir')}, "
            f"Boss HP: {context.get('boss_hp')}/{context.get('boss_max_hp')}, "
            f"Player HP: {context.get('player_hp')}/{context.get('player_max_hp')}. "
            "Generate a single short boss taunt line in ALL CAPS."
        )

        def worker():
            text = fallback
            try:
                interaction = self._client.interactions.create(
                    model="gemini-3.5-flash-lite",
                    system_instruction=SYSTEM_INSTRUCTION,
                    input=prompt,
                )
                if getattr(interaction, "output_text", None):
                    cleaned = " ".join(interaction.output_text.strip().split()).upper()
                    cleaned = cleaned.strip("\"'")
                    if cleaned:
                        text = cleaned[:115]
            except Exception:
                text = fallback
            finally:
                with self._lock:
                    self._pending_text = text
                    self._request_in_flight = False

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def _format_fallback(category, context):
        templates = FALLBACK_TAUNTS.get(category, FALLBACK_TAUNTS["intro"])
        template = random.choice(templates)
        return template.format(
            temp=context.get("temp") if context.get("temp") is not None else 27,
            light=context.get("light") if context.get("light") is not None else 0,
            dir=str(context.get("dir", "left")).upper(),
            boss_hp=context.get("boss_hp", 100),
            player_hp=context.get("player_hp", 1),
        )

    def _start_display(self, text):
        self.full_text = text.upper()
        self.visible_chars = 0.0
        self.last_blip_char = 0
        self.hold_timer = self.HOLD_DURATION
        self.active = True
        self.cooldown = self.COOLDOWN_DURATION

    def update(self, dt, session, serial_data):
        with self._lock:
            if self._pending_text is not None:
                self._start_display(self._pending_text)
                self._pending_text = None

        if self.active:
            total_len = len(self.full_text)
            if self.visible_chars < total_len:
                self.visible_chars = min(
                    float(total_len),
                    self.visible_chars + self.CHAR_SPEED * dt,
                )
                current_idx = int(self.visible_chars)
                if current_idx > self.last_blip_char:
                    new_char = self.full_text[current_idx - 1]
                    # Play Pokemon-style dialogue blip every 2 non-space characters
                    if new_char != " " and (current_idx - self.last_blip_char >= 2 or self.last_blip_char == 0):
                        if self.audio is not None:
                            self.audio.play("dialogue_blip")
                        self.last_blip_char = current_idx
            else:
                self.hold_timer -= dt
                if self.hold_timer <= 0:
                    self.active = False
            return

        self.cooldown = max(0.0, self.cooldown - dt)
        if self.cooldown > 0 or self._request_in_flight:
            return

        temp = serial_data.get("temp")
        light = serial_data.get("light")
        direction = serial_data.get("dir", "none")
        boss = session.boss
        player = session.player

        context = {
            "temp": temp,
            "light": light,
            "dir": direction,
            "boss_hp": boss.health,
            "boss_max_hp": boss.max_health,
            "player_hp": player.health,
            "player_max_hp": player.max_health,
        }

        is_hot = False
        try:
            is_hot = float(temp) > 26.0
        except (TypeError, ValueError):
            pass

        is_dark = False
        try:
            is_dark = float(light) < 85.0
        except (TypeError, ValueError):
            pass

        if not self._seen_intro:
            self._seen_intro = True
            self.trigger_taunt("intro", context)
        elif is_hot and not self._was_hot:
            self._was_hot = True
            self.trigger_taunt("fire", context)
        elif is_dark and not self._was_dark:
            self._was_dark = True
            self.trigger_taunt("dark", context)
        elif boss.health <= boss.max_health * 0.4 and not self._was_boss_low:
            self._was_boss_low = True
            self.trigger_taunt("boss_low", context)
        elif player.health <= 2 and not self._was_player_low:
            self._was_player_low = True
            self.trigger_taunt("player_low", context)
        elif direction in ("left", "right"):
            self.trigger_taunt("tilt", context)
        elif getattr(boss, "lasers", None):
            self.trigger_taunt("laser", context)
        elif is_hot:
            self.trigger_taunt("fire", context)

        if not is_hot:
            self._was_hot = False
        if not is_dark:
            self._was_dark = False

    def _wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if self.body_font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines[:2]

    def draw(self, screen):
        if not self.active or not self.full_text:
            return

        # Outer shadow + Pokemon-style double pixel border
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(screen, PALETTE["shadow"], shadow_rect)
        pygame.draw.rect(screen, PALETTE["panel"], self.rect)
        pygame.draw.rect(screen, PALETTE["cream"], self.rect, 4)

        inner_border = self.rect.inflate(-12, -12)
        pygame.draw.rect(screen, PALETTE["panel_light"], inner_border, 2)

        # Speaker nameplate tab at top-left of the Pokemon box
        tag_rect = pygame.Rect(self.rect.left + 20, self.rect.top - 14, 130, 24)
        pygame.draw.rect(screen, PALETTE["panel"], tag_rect)
        pygame.draw.rect(screen, PALETTE["ember"], tag_rect, 2)
        tag_label = self.small_font.render("BOSS", False, PALETTE["ember"])
        screen.blit(tag_label, tag_label.get_rect(center=tag_rect.center))

        # Slice revealed text and wrap across 2 lines
        revealed = self.full_text[: int(self.visible_chars)]
        max_text_width = inner_border.width - 36
        lines = self._wrap_text(revealed, max_text_width)

        for idx, line in enumerate(lines):
            surf = self.body_font.render(line, False, PALETTE["cream"])
            screen.blit(
                surf,
                (inner_border.left + 16, inner_border.top + 14 + idx * 30),
            )

        # Classic Pokemon bouncing triangle prompt once typing completes
        if int(self.visible_chars) >= len(self.full_text):
            bounce = 3 if int(pygame.time.get_ticks() / 220) % 2 == 0 else 0
            ax = inner_border.right - 20
            ay = inner_border.bottom - 16 + bounce
            pygame.draw.polygon(
                screen,
                PALETTE["ember"],
                [(ax - 7, ay - 5), (ax + 7, ay - 5), (ax, ay + 4)],
            )
