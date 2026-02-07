import pygame
import os
import random

# Initialize mixer (do this once at game start)
pygame.mixer.init()

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
    folder = f"assets/audio/Boss{boss_id}"
    # Collect all voiceline files (excluding the intro)
    files = [f for f in os.listdir(folder) if f.lower().endswith(".wav") and "Voiceline" in f]
    if not files:
        print(f"No voicelines found for boss {boss_id}")
        return
    file_path = os.path.join(folder, random.choice(files))
    play_audio_clip(file_path)
