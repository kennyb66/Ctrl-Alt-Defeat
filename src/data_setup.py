import os
import pygame
from src.entities import Student, Professor


def create_roster(sprite_dir: str) -> list[Student]:
    roster = [
        Student(
            "Cs Get Degrees", 100, 15,
            "Hidden Ability: 25% chance to ignore a wrong answer on a dodge.",
            "C's Really Do Get Degrees! You passed!",
            sprite_folder=os.path.join(sprite_dir, "swi", "standard", "idle", "right"),
            idle_frames=2,
        ),
        Student(
            "4.0 Medallion", 100, 20,
            "Special: 20% Critical Hit chance (The Curve) for 1.5x damage.",
            "Academic Excellence!",
            sprite_folder=os.path.join(sprite_dir, "kris", "standard", "idle", "right"),
            idle_frames=2,
        ),
        Student(
            "TA God", 100, 18,
            "Special: Healing restores twice as much HP (Lab Snacks).",
            "The lab is yours now!",
            sprite_folder=os.path.join(sprite_dir, "ken", "standard", "idle", "right"),
            idle_frames=2,
        ),
    ]

    hover_paths = [
        os.path.join(sprite_dir, "swi", "standard", "thrust", "left", "3.png"),
        os.path.join(sprite_dir, "kris", "standard", "thrust", "left", "3.png"),
        os.path.join(sprite_dir, "ken", "standard", "thrust", "left", "3.png"),
    ]
    for student, path in zip(roster, hover_paths):
        student.hover_path = path
        try:
            student.hover_sprite = pygame.image.load(path).convert_alpha()
        except Exception:
            student.hover_sprite = None

    return roster


def create_profs(sprite_dir: str) -> list[Professor]:
    return [
        Professor(
            "Prof Sridhar", 150, 35,
            "Logic is not O(1). You fail Data Structures.",
            "The Biz", bossId=1,
            sprite_folder=os.path.join(sprite_dir, "sridhar", "standard", "idle", "left"),
            idle_frames=2,
        ),
        Professor(
            "Prof Diochnos", 200, 35,
            "This language is not decidable\u2026 and neither are you. You fail Theory.\u201d",
            "Turing Machine Terrace", bossId=2,
            sprite_folder=os.path.join(sprite_dir, "dioch", "standard", "idle", "left"),
            idle_frames=2,
        ),
        Professor(
            "Prof Maiti", 275, 35,
            "Your hash has collisions. You fail Cryptography.",
            "Bitcoin Boulevard", bossId=3,
            sprite_folder=os.path.join(sprite_dir, "maiti", "standard", "idle", "left"),
            idle_frames=2,
        ),
    ]