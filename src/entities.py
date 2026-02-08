import pygame
import random
import math
from src.constants import *
import os

class AnimatedEntity:
    def __init__(self, name, hp, attack_power, color, sprite_folder=None,
                 idle_frames=2, action_frames=1, scale=3, animation_speed=400):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack_power = attack_power
        self.color = color

        self.state = IDLE

        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = animation_speed
        self.offset_y = 0

        # Frames: dictionary keyed by state
        self.frames = {IDLE: [], ACTION: []}

        # Load idle frames from folder
        if sprite_folder:
            # Sort files to ensure proper frame order
            files = sorted([f for f in os.listdir(sprite_folder) if f.endswith(".png")])
            if not files:
                raise ValueError(f"No PNGs found in {sprite_folder}")
            for f in files:
                path = os.path.join(sprite_folder, f)
                img = pygame.image.load(path).convert_alpha()
                # scale it bigger
                w, h = img.get_size()
                img = pygame.transform.scale(img, (w * scale, h * scale))
                self.frames[IDLE].append(img)            
            # Placeholder empty action frames
            self.frames[ACTION] = [pygame.Surface(self.frames[IDLE][0].get_size(), pygame.SRCALPHA) for _ in range(action_frames)]

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()

    def update_animation(self):
        now = pygame.time.get_ticks()
        if self.state == IDLE:
            #this was a "bounce" for rectangles to mimic idling
           ## self.offset_y = math.sin(now / 200) * 10
            if now - self.last_update > self.animation_speed:
                if self.frames[IDLE]:
                    self.frame_index = (self.frame_index + 1) % len(self.frames[IDLE])
                self.last_update = now
        elif self.state == ACTION:
            if now - self.last_update > 100:
                if self.frames[ACTION]:
                    self.frame_index = (self.frame_index + 1) % len(self.frames[ACTION])
                self.last_update = now
                if self.frame_index == 0:
                    self.set_state(IDLE)



    def draw(self, screen, x, y):
        self.update_animation()
        if self.frames.get(self.state) and len(self.frames[self.state]) > 0:
            frame = self.frames[self.state][self.frame_index]
            #screen.blit(frame, (x, y + self.offset_y)) #offset_y was for rectangle bounce 
            screen.blit(frame, (x, y))
        else:
            #fallback rect if frames fail
            rect_height = 200 if self.state == IDLE else 180
            color = self.color if self.state == IDLE else WHITE
            pygame.draw.rect(screen, color, (x, y + self.offset_y, 150, rect_height), border_radius=10)

            '''
        # Drawing a rectangle as a placeholder for the sprite
        # In a real game, you'd blit: screen.blit(self.frames[self.state][self.frame_index], (x, y + self.offset_y))
        rect_height = 200 if self.state == IDLE else 180
        color = self.color if self.state == IDLE else WHITE
        pygame.draw.rect(screen, color, (x, y + self.offset_y, 150, rect_height), border_radius=10)
        # Eye level indicator to see "bouncing"
        pygame.draw.rect(screen, BLACK, (x + 30, y + self.offset_y + 40, 20, 20))
        pygame.draw.rect(screen, BLACK, (x + 100, y + self.offset_y + 40, 20, 20))
        '''

class Student(AnimatedEntity):
    def __init__(self, name, hp, attack_power, ability_desc, win_msg,
                 sprite_folder=None, idle_frames=2, action_frames=1,
                 scale=3, animation_speed=600,numHeals=1):
        # Pass everything to AnimatedEntity
        super().__init__(name, hp, attack_power, GREEN,
                         sprite_folder=sprite_folder,
                         idle_frames=idle_frames,
                         action_frames=action_frames,
                         scale=scale,
                         animation_speed=animation_speed)

        self.numHeals = numHeals
        self.ability_desc = ability_desc
        self.win_msg = win_msg
        self.current_speech = ""
        self.speech_timer = 0


    def say(self, text):
        """Sets the text and starts a 2-second timer."""
        self.current_speech = text
        self.speech_timer = pygame.time.get_ticks() + 2000 

    def calculate_attack(self):
        self.set_state(ACTION)

        roll = random.random()
        crit_chance = 0.20 if self.name == "4.0 Medallion" else 0.05
        
        if roll < crit_chance:
            msg = "CRITICAL HIT! (The Curve effect!)"
            return int(self.attack_power * 1.5), msg
        elif roll < crit_chance + 0.15:
            msg = "Glancing hit... barely passed."
            return int(self.attack_power * 0.5), msg
        return self.attack_power, "Direct Hit!"

    def get_heal_amount(self):
        self.set_state(ACTION)

        base = 35
        if self.name == "TA God":
            return int(base * 2), "SPECIAL: Lab snacks! Double Healing!"
        return base, f"Studied hard. Restored {base} HP."

class Professor(AnimatedEntity):
    def __init__(self, name, hp, attack_power, loss_msg, level_name, bossId,
                 sprite_folder=None, idle_frames=2, action_frames=1,
                 scale=3, animation_speed=600):
        super().__init__(name, hp, attack_power, OU_CRIMSON,
                         sprite_folder=sprite_folder,
                         idle_frames=idle_frames,
                         action_frames=action_frames,
                         scale=scale,
                         animation_speed=animation_speed)
        self.loss_msg = loss_msg
        self.level_name = level_name
        self.bossId = bossId

