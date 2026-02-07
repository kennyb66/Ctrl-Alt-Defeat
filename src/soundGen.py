import pygame
import os
import random

pygame.mixer.init()

# Path to the project root (Ctrl-Alt-Defeat folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")


def play_audio_clip(file_path, volume=1.0):
    """Plays a single sound clip (.wav) asynchronously."""
    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return

    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    sound.play()


def play_random_voiceline(boss_id):
    """Plays a random question voiceline for a given boss."""

    # Absolute path to Boss folder
    folder = os.path.join(AUDIO_DIR, f"Boss{boss_id}")

    if not os.path.exists(folder):
        print(f"Boss audio folder missing: {folder}")
        return

    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".wav") and "voiceline" in f.lower()
    ]

    if not files:
        print(f"No voicelines found for boss {boss_id} in {folder}")
        return

    file_path = os.path.join(folder, random.choice(files))
    play_audio_clip(file_path)
