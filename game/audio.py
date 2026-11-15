import os

import pygame


class GameAudio:
    """Small, optional audio wrapper for one-shot effects and gameplay music."""

    SOUND_FILES = {
        "player_attack_hit": "player_attack_hit.mp3",
        "player_miss": "player_attack_miss.mp3",
        "boss_attack": "boss_hit_sword.mp3",
        "boss_miss": "boss_miss_sword.mp3",
        "dash": "dash.mp3",
        "walking": "Walking.mp3",
    }

    def __init__(self, sound_directory=None):
        if sound_directory is None:
            sound_directory = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "assets", "sound")
            )

        self.sound_directory = sound_directory
        self.sounds = {}
        self.music_path = os.path.join(sound_directory, "GameplaySoundtrack.wav")
        self.music_loaded = False
        self.enabled = False

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            return

        for name, filename in self.SOUND_FILES.items():
            if filename is not None:
                self._load_sound(name, os.path.join(sound_directory, filename))

        if os.path.isfile(self.music_path):
            try:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.set_volume(0.1)
                self.music_loaded = True
            except pygame.error:
                self.music_loaded = False

    def _load_sound(self, name, path):
        if not os.path.isfile(path):
            return
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.5)
            self.sounds[name] = sound
        except pygame.error:
            return

    def load_sound(self, name, path, volume=0.5):
        """Load an additional optional sound, such as the weather wind effect."""
        if not self.enabled or not os.path.isfile(path):
            return None
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.sounds[name] = sound
            return sound
        except pygame.error:
            return None

    def play(self, name):
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def start_gameplay_music(self):
        if self.enabled and self.music_loaded and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(loops=-1)

    def stop_gameplay_music(self):
        if self.enabled:
            pygame.mixer.music.stop()
