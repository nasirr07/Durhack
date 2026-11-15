import json
import os
import random
import threading
import urllib.request
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
        "THE SCREEN RUMBLES! MY FALLING BOULDERS WILL CRUSH YOU!",
        "SHAKING THE MICROBIT?! FEEL THE ARENA TREMBLE AND COLLAPSE!",
        "EARTHQUAKE! WATCH THE CEILING CRUMBLE ABOVE YOUR HEAD!",
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
        self._rest_model = None
        self.api_key = _resolve_api_key()
        if genai is not None and self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

        if self.api_key:
            print("[BossTauntBox] Gemini API key loaded successfully.")
        else:
            print("[BossTauntBox] No GEMINI_API_KEY found (.env or taunts.py) - using fallback taunts.")

        self._lock = threading.Lock()
        self._pending_text = None
        self._pending_source = "FALLBACK"
        self._request_in_flight = False
        self.source = "FALLBACK"
        self.reset()

    def reset(self):
        with self._lock:
            self._pending_text = None
            self._pending_source = "FALLBACK"
        self.full_text = ""
        self.source = "FALLBACK"
        self.visible_chars = 0.0
        self.last_blip_char = 0
        self.hold_timer = 0.0
        self.active = False
        self.cooldown = 0.6
        self._seen_intro = False
        self._was_hot = False
        self._was_dark = False
        self._was_rumbling = False
        self._was_boss_low = False
        self._was_player_low = False

    def _resolve_rest_model(self):
        if self._rest_model:
            return self._rest_model

        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        req = urllib.request.Request(list_url, method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        available = []
        for m in data.get("models", []):
            methods = m.get("supportedGenerationMethods", [])
            name = m.get("name", "")  # e.g. "models/gemini-..."
            if "generateContent" in methods and name.startswith("models/"):
                short = name.split("/", 1)[1]
                if "tts" not in short and "image" not in short and "embedding" not in short:
                    available.append(short)

        # Prefer fast flash-lite / flash / hydrogen models
        preferred_substrings = (
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-4-hydrogen",
            "flash-lite",
            "flash",
            "gemini",
        )
        for pref in preferred_substrings:
            for model_name in available:
                if pref in model_name:
                    self._rest_model = model_name
                    print(f"[BossTauntBox] Using Gemini model: {self._rest_model}")
                    return self._rest_model

        if available:
            self._rest_model = available[0]
            print(f"[BossTauntBox] Using Gemini model: {self._rest_model}")
            return self._rest_model

        self._rest_model = "gemini-3.5-flash-lite"
        return self._rest_model

    def _call_gemini(self, prompt):
        """Call Gemini via google-genai SDK if installed, or direct HTTPS REST with stdlib urllib."""
        if self._client is not None:
            interaction = self._client.interactions.create(
                model="gemini-3.5-flash-lite",
                system_instruction=SYSTEM_INSTRUCTION,
                input=prompt,
            )
            if getattr(interaction, "output_text", None):
                return interaction.output_text

        model_name = self._resolve_rest_model()
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={self.api_key}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{SYSTEM_INSTRUCTION}\n\n{prompt}"}],
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 200,
                "temperature": 0.9,
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=6.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    if not part.get("thought") and part.get("text"):
                        return part["text"]
        return None

    def trigger_taunt(self, category, context):
        """Queue a Gemini API taunt request in a background thread (with instant fallback support)."""
        if self._request_in_flight:
            return

        # Re-check key in case .env was edited before gameplay started
        if not self.api_key:
            self.api_key = _resolve_api_key()

        fallback = self._format_fallback(category, context)
        if not self.api_key:
            print(f"[Taunt | FALLBACK] {fallback} (no GEMINI_API_KEY set)")
            self._start_display(fallback, source="FALLBACK")
            return

        self._request_in_flight = True
        event_desc = (
            "EARTHQUAKE RUMBLE! The screen is violently shaking and boulders are falling from the ceiling because the player shook/tilted the micro:bit"
            if category == "tilt"
            else category
        )
        prompt = (
            f"Event: {event_desc}. "
            f"Room temperature: {context.get('temp')}C, "
            f"Light sensor: {context.get('light')}/255, "
            f"Tilt direction: {context.get('dir')}, "
            f"Screen rumbling: {context.get('rumbling', False)}, "
            f"Boss HP: {context.get('boss_hp')}/{context.get('boss_max_hp')}, "
            f"Player HP: {context.get('player_hp')}/{context.get('player_max_hp')}. "
            "Generate a single short boss taunt line in ALL CAPS reacting to this event."
        )

        def worker():
            text = fallback
            source = "FALLBACK"
            try:
                raw_output = self._call_gemini(prompt)
                if raw_output:
                    cleaned = " ".join(raw_output.strip().split()).upper()
                    cleaned = cleaned.strip("\"'")
                    if cleaned:
                        text = cleaned[:115]
                        source = "GEMINI AI"
                        print(f"[Taunt | GEMINI AI] {text}")
                else:
                    print(f"[Taunt | FALLBACK] {fallback} (empty Gemini response)")
            except Exception as exc:
                print(f"[Taunt | FALLBACK] {fallback} (Gemini error: {exc})")
                text = fallback
                source = "FALLBACK"
            finally:
                with self._lock:
                    self._pending_text = text
                    self._pending_source = source
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

    def _start_display(self, text, source="FALLBACK"):
        self.full_text = text.upper()
        self.source = source
        self.visible_chars = 0.0
        self.last_blip_char = 0
        self.hold_timer = self.HOLD_DURATION
        self.active = True
        self.cooldown = self.COOLDOWN_DURATION

    def update(self, dt, session, serial_data):
        with self._lock:
            if self._pending_text is not None:
                self._start_display(self._pending_text, source=self._pending_source)
                self._pending_text = None

        temp = serial_data.get("temp")
        light = serial_data.get("light")
        direction = serial_data.get("dir", "none")
        boss = session.boss
        player = session.player
        hazard = getattr(session, "hazard", None)
        phase_val = getattr(getattr(hazard, "phase", None), "value", "idle")
        is_rumbling = phase_val in ("warning", "boulders") or (
            getattr(hazard, "shake_offset", (0, 0)) != (0, 0)
        )

        context = {
            "temp": temp,
            "light": light,
            "dir": direction,
            "rumbling": is_rumbling,
            "boss_hp": boss.health,
            "boss_max_hp": boss.max_health,
            "player_hp": player.health,
            "player_max_hp": player.max_health,
        }

        # Immediately react as soon as screen rumbling / earthquake starts (even if cooldown is active)
        if is_rumbling and not self._was_rumbling:
            self._was_rumbling = True
            self.trigger_taunt("tilt", context)
        elif not is_rumbling:
            self._was_rumbling = False

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

        # Speaker nameplate tab at top-left of the Pokemon box (shows GEMINI AI vs FALLBACK)
        is_gemini = self.source == "GEMINI AI"
        badge_colour = PALETTE["wind"] if is_gemini else PALETTE["ember"]
        badge_text = "BOSS [GEMINI AI]" if is_gemini else "BOSS [FALLBACK]"
        tag_label = self.small_font.render(badge_text, False, badge_colour)
        tag_width = max(140, tag_label.get_width() + 24)
        tag_rect = pygame.Rect(self.rect.left + 20, self.rect.top - 14, tag_width, 24)
        pygame.draw.rect(screen, PALETTE["panel"], tag_rect)
        pygame.draw.rect(screen, badge_colour, tag_rect, 2)
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
