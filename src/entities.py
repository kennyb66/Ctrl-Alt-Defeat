import pygame
import random
import math
from src.constants import *
import os

class AnimatedEntity:
    def __init__(self, name, hp, attack_power, color, sprite_folder=None,
                 idle_frames=2, action_frames=1, scale=5, animation_speed=400):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack_power = attack_power
        self.color = color
        self.scale = scale
        self.idle_frames = idle_frames
        self.action_frames = action_frames
        self.state = IDLE

        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = animation_speed
        self.offset_y = 0
        self.override_frames = None
        self.override_index = 0
        self.override_speed = 120
        self.override_loop = False # This was the specific one causing your last error
        self.freeze_last_frame = False
        self.is_dead = False
        
        self.facing = "right" 
        # Ensure sprite_folder exists before trying to get base_path
        if sprite_folder:
            self.base_sprite_folder = sprite_folder

            self.base_path = os.path.dirname(os.path.dirname(sprite_folder)) 
            self.all_frames = {
                "right": {IDLE: [], WALK: [], ACTION: []},
                "left": {IDLE: [], WALK: [], ACTION: []}
            }
            # This handles all the heavy lifting of loading PNGs
            self.load_all_directions()
            
            # Fill ACTION frames with empty surfaces if they weren't loaded
            for d in ["left", "right"]:
                if self.all_frames[d][IDLE]:
                    size = self.all_frames[d][IDLE][0].get_size()
                    if not self.all_frames[d][ACTION]:
                        self.all_frames[d][ACTION] = [pygame.Surface(size, pygame.SRCALPHA) for _ in range(action_frames)]
            
            self.current_frame = 0
            self.last_frame_time = pygame.time.get_ticks()

        # Animation state systems
        self.override_frames = None
        self.override_index = 0
        self.freeze_last_frame = False
        self.is_dead = False

          
    def load_all_directions(self):
        for d in ["left", "right"]:
            # Load Idle
            path = os.path.join(self.base_path, "idle", d)
            if os.path.exists(path):
                self.all_frames[d][IDLE] = self.load_frames(path, self.idle_frames)
            # Load Walk
            path = os.path.join(self.base_path, "walk", d)
            if os.path.exists(path):
                self.all_frames[d][WALK] = self.load_frames(path, self.idle_frames) # assuming same frame count
    def load_frames(self, folder, frame_count):
        frames = []
        for i in range(1, frame_count + 1):
            img = pygame.image.load(os.path.join(folder, f"{i}.png")).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width()*self.scale, img.get_height()*self.scale))
            frames.append(img)
        return frames

    def play_animation(self, action_name, direction, frame_count, freeze_last=False):        # Example: idle/right → hurt/up
        base = os.path.dirname(os.path.dirname(self.base_sprite_folder))
        anim_path = os.path.join(base, action_name, direction)
    
        if os.path.exists(anim_path):
            frames = []
            files = sorted([f for f in os.listdir(anim_path) if f.endswith(".png")])
            for f in files:
                img = pygame.image.load(os.path.join(anim_path, f)).convert_alpha()
                w, h = img.get_size()
                img = pygame.transform.scale(img, (int(w * self.scale), int(h * self.scale)))
                frames.append(img)
            
            self.override_frames = frames
            self.override_index = 0
            self.freeze_last_frame = freeze_last
            

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0
            self.current_frame = 0  # ADD THIS LINE - reset frame index
            self.last_update = pygame.time.get_ticks()
            self.last_frame_time = pygame.time.get_ticks()  # ADD THIS TOO for consistency

    def update_animation(self):
        now = pygame.time.get_ticks()

        # If playing temporary animation
        if self.override_frames:
            # If frozen, just stay on last frame forever
            if self.freeze_last_frame and self.override_index >= len(self.override_frames) - 1:
                self.override_index = len(self.override_frames) - 1
                return  # Don't advance, stay frozen
            
            if now - self.last_frame_time > self.override_speed:
                self.override_index += 1
                self.last_frame_time = now
                if self.override_index >= len(self.override_frames):
                    if self.override_loop:
                        self.override_index = 0
                    else:
                        self.override_frames = None
                        self.override_index = 0
            return
        
        # State-based animation (IDLE or WALK)
        current_dir_frames = self.all_frames[self.facing]
        current_frames = current_dir_frames.get(self.state, current_dir_frames[IDLE])
        if now - self.last_frame_time > self.animation_speed:
            if len(current_frames) > 0:
                self.current_frame = (self.current_frame + 1) % len(current_frames)
            self.last_frame_time = now

    def update(self):
        self.update_animation()
        
    def draw(self, screen, x, y):
        if not (self.freeze_last_frame and self.override_frames and 
                self.override_index >= len(self.override_frames) - 1):
            self.update_animation()
        
        if self.override_frames:
            # Safety check for override frames
            if self.override_index >= len(self.override_frames):
                self.override_index = len(self.override_frames) - 1
            frame = self.override_frames[self.override_index]
        else:
            current_dir_frames = self.all_frames[self.facing]
            current_frames = current_dir_frames.get(self.state, current_dir_frames[IDLE])
            
            # Safety check: ensure current_frames exists and has frames
            if not current_frames:
                current_frames = current_dir_frames[IDLE]
            
            # Safety check: ensure current_frame is within bounds
            if self.current_frame >= len(current_frames):
                self.current_frame = 0
            
            # Final safety check before accessing
            if len(current_frames) == 0:
                # Create a dummy frame if no frames exist
                frame = self.all_frames[self.facing][IDLE][0] if self.all_frames[self.facing][IDLE] else pygame.Surface((64, 64))
            else:
                frame = current_frames[self.current_frame]
        
        screen.blit(frame, (x, y))
class Student(AnimatedEntity):
    def __init__(self, name, hp, attack_power, ability_desc, win_msg,
                 sprite_folder=None, idle_frames=2, action_frames=1,
                 scale=5, animation_speed=300,numHeals=1):
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
      #  self.set_state(ACTION)

        roll = random.random()
        crit_chance = 0.20 if self.name == "4.0 Medallion" else 0.05
        
        if roll < crit_chance:
            if self.name == "4.0 Medallion":
                msg = "CRITICAL HIT!\n(The Curve effect!)"
                return int(self.attack_power * 1.5), msg, True
            else:
                msg = "CRITICAL HIT!"
                return int(self.attack_power * 1.5), msg, False
        elif roll < crit_chance + 0.15:
            msg = "BLOCKED!\nPartial Hit."
            return int(self.attack_power * 0.5), msg, False
        return self.attack_power, "Direct Hit!", False

    def get_heal_amount(self):
      #  self.set_state(ACTION)

        base = 35
        if self.name == "TA God":
            return int(base * 2), "SPECIAL:\nLab snacks! Double Healing!", True
        return base, f"Studied hard. Restored {base} HP.", False

class Professor(AnimatedEntity):
    def __init__(self, name, hp, attack_power, loss_msg, level_name, bossId,
                 sprite_folder=None, idle_frames=2, action_frames=1,
                 scale=6, animation_speed=350):
        super().__init__(name, hp, attack_power, OU_CRIMSON,
                         sprite_folder=sprite_folder,
                         idle_frames=idle_frames,
                         action_frames=action_frames,
                         scale=scale,
                         animation_speed=animation_speed)
        self.loss_msg = loss_msg
        self.level_name = level_name
        self.bossId = bossId

