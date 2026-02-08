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
        self.state = IDLE

        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = animation_speed
        self.offset_y = 0

        # Frames: dictionary keyed by state
        self.frames = {IDLE: [], ACTION: [], WALK: []}


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

                # ---- Load WALK frames automatically ----
            walk_folder = sprite_folder.replace("idle", "walk")
            if os.path.exists(walk_folder):
                walk_files = sorted([f for f in os.listdir(walk_folder) if f.endswith(".png")])
                for f in walk_files:
                    path = os.path.join(walk_folder, f)
                    img = pygame.image.load(path).convert_alpha()
                    w, h = img.get_size()
                    img = pygame.transform.scale(img, (w * scale, h * scale))
                    self.frames[WALK].append(img)
                        
            # Placeholder empty action frames
            self.frames[ACTION] = [pygame.Surface(self.frames[IDLE][0].get_size(), pygame.SRCALPHA) for _ in range(action_frames)]

            self.base_sprite_folder = sprite_folder   # idle/right etc
            self.idle_frames = idle_frames

            self.anim_frames = self.load_frames(sprite_folder, idle_frames)
            self.current_frame = 0
            self.last_frame_time = pygame.time.get_ticks()

            # NEW animation override system
            self.override_frames = None
            self.override_index = 0
            self.override_speed = 120
            self.override_loop = False
            self.freeze_last_frame = False
            self.is_dead = False

    def load_frames(self, folder, frame_count):
        frames = []
        for i in range(1, frame_count + 1):
            img = pygame.image.load(os.path.join(folder, f"{i}.png")).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width()*self.scale, img.get_height()*self.scale))
            frames.append(img)
        return frames

    def play_animation(self, subfolder, direction, frame_count, speed=120, loop=False, freeze_last=False):
        # Example: idle/right → hurt/up
        base = os.path.dirname(os.path.dirname(self.base_sprite_folder))
        path = os.path.join(base, subfolder, direction)

        self.override_frames = self.load_frames(path, frame_count)
        self.override_index = 0
        self.override_speed = speed
        self.override_loop = loop
        self.freeze_last_frame = freeze_last
        self.last_frame_time = pygame.time.get_ticks()

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

                # animation finished
                if self.override_index >= len(self.override_frames):
                    if self.freeze_last_frame:
                        self.override_index = len(self.override_frames) - 1
                        return  # Stay frozen on last frame
                    elif self.override_loop:
                        self.override_index = 0
                    else:
                        self.override_frames = None
                        self.override_index = 0
            return
        
        # State-based animation (IDLE or WALK)
        current_frames = self.frames.get(self.state, self.frames[IDLE])
        if now - self.last_frame_time > self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(current_frames)
            self.last_frame_time = now

    def draw(self, screen, x, y):
        self.update_animation()

        if self.override_frames:
            frame = self.override_frames[self.override_index]
        else:
            # Use frames based on current state
            current_frames = self.frames.get(self.state, self.frames[IDLE])
            
            # Safety check to prevent index errors
            if self.current_frame >= len(current_frames):
                self.current_frame = 0
            
            frame = current_frames[self.current_frame]

        screen.blit(frame, (x, y))


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
            return int(base * 2), "SPECIAL: Lab snacks! Double Healing!", True
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

