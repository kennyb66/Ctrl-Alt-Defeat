import pygame
import random
import math
from src.constants import *

class AnimatedEntity:
    def __init__(self, name, hp, attack_power, color):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack_power = attack_power
        self.color = color
        
        # Animation logic
        self.state = IDLE
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 150 # ms per frame
        self.offset_y = 0 # For the "idle bounce"

    def update_animation(self):
        now = pygame.time.get_ticks()
        # Idle Bounce (sine wave)
        if self.state == IDLE:
            self.offset_y = math.sin(now / 200) * 10
            if now - self.last_update > self.animation_speed:
                self.frame_index = (self.frame_index + 1) % 3 # 3 idle frames
                self.last_update = now
        # Action Animation
        elif self.state == ACTION:
            if now - self.last_update > 100: # Action is faster
                self.frame_index += 1
                if self.frame_index >= 5: # 5 action frames
                    self.frame_index = 0
                    self.state = IDLE
                self.last_update = now

    def draw(self, screen, x, y):
        self.update_animation()
        # Drawing a rectangle as a placeholder for the sprite
        # In a real game, you'd blit: screen.blit(self.frames[self.state][self.frame_index], (x, y + self.offset_y))
        rect_height = 200 if self.state == IDLE else 180
        color = self.color if self.state == IDLE else WHITE
        pygame.draw.rect(screen, color, (x, y + self.offset_y, 150, rect_height), border_radius=10)
        # Eye level indicator to see "bouncing"
        pygame.draw.rect(screen, BLACK, (x + 30, y + self.offset_y + 40, 20, 20))
        pygame.draw.rect(screen, BLACK, (x + 100, y + self.offset_y + 40, 20, 20))

class Student(AnimatedEntity):
    def __init__(self, name, hp, attack_power, ability_desc, win_msg):
        super().__init__(name, hp, attack_power, GREEN)
        self.ability_desc = ability_desc
        self.win_msg = win_msg

    def calculate_attack(self):
        self.state = ACTION
        roll = random.random()
        crit_chance = 0.20 if self.name == "4.0 Medallion" else 0.05
        glance_chance = 0.15
        
        if roll < crit_chance:
            return int(self.attack_power * 1.5), "CRITICAL HIT! (The Curve)"
        elif roll < crit_chance + glance_chance:
            return int(self.attack_power * 0.5), "Glancing hit..."
        else:
            return self.attack_power, "Direct Hit!"

    def get_heal_amount(self):
        self.state = ACTION
        base = 25
        return int(base * 1.5) if self.name == "TA God" else base

class Professor(AnimatedEntity):
    def __init__(self, name, hp, attack_power, loss_msg, level_name, bossId):
        super().__init__(name, hp, attack_power, OU_CRIMSON)
        self.loss_msg = loss_msg
        self.level_name = level_name
        self.bossId = bossId