import pygame
import os
import random

class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        # Dedicated channels
        self.voice_channel = pygame.mixer.Channel(0)
        self.sfx_channel   = pygame.mixer.Channel(1)

        # Base paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.audio_dir = os.path.join(base_dir, "assets", "audio")

    # -------------------------
    # Core voice playback
    # -------------------------
    def play_voice(self, file_path, volume=1.0, fade_ms=150):
        if not os.path.exists(file_path):
            print(f"[WARN] Missing audio file: {file_path}")
            return

        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(volume)

        if self.voice_channel.get_busy():
            self.voice_channel.fadeout(fade_ms)

        self.voice_channel.play(sound)

    # -------------------------
    # Random question voiceline
    # -------------------------
    def play_random_voiceline(self, boss_id):
        folder = os.path.join(self.audio_dir, f"Boss{boss_id}")

        if not os.path.exists(folder):
            print(f"[WARN] Boss audio folder missing: {folder}")
            return

        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith(".wav") and "voiceline" in f.lower()
        ]

        if not files:
            print(f"[WARN] No voicelines for boss {boss_id}")
            return

        file_path = os.path.join(folder, random.choice(files))
        self.play_voice(file_path)