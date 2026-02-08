import math
import pygame
import random
import os
from src.constants import *
from src.entities import Student, Professor
from src.ui import Button, draw_text, draw_speech_bubble, wrap_text
from src.dataGen import load_questions
from src.dataGen import QuestionManager
from src.soundGen import SoundManager


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
SPRITE_DIR = os.path.join(BASE_DIR, "assets", "characters")
SFX_DIR = os.path.join(BASE_DIR, "assets", "audio", "sfx")

pygame.init()
pygame.mixer.init()  # This is required to play sounds

class Game:
    def __init__(self):
        self.sound = SoundManager()

        # Center the window on all platforms (Windows, macOS, Linux)
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        self.flash_timer = 0
        # Get actual screen dimensions after fullscreen is set (fixes Windows centering)
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH = self.screen.get_width()
        SCREEN_HEIGHT = self.screen.get_height()
        # Responsive fonts
        self.font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.025))
        self.title_font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.07), bold=True)
        self.medium_font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.035), bold=True)
        self.small_font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.02))
        
        # Load background images
        scroll_path = os.path.join(BASE_DIR, "assets", "backgrounds", "scroll.png")
        self.scroll_bg = pygame.image.load(scroll_path)
        self.scroll_bg = pygame.transform.scale(self.scroll_bg, (int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.65)))
        

        # Load custom cursor image
        self.custom_cursor = None
        cursor_path = os.path.join(BASE_DIR, "assets", "ui", "mouse cursor.png")

        if os.path.exists(cursor_path):
            try:
                self.custom_cursor = pygame.image.load(cursor_path)
                self.custom_cursor = pygame.transform.scale(self.custom_cursor, (32, 32))
                self.custom_cursor = self.custom_cursor.convert_alpha()  # Optimize for fast blitting
                pygame.mouse.set_visible(False)  # Hide default cursor
            except Exception as e:
                print(f"Error loading cursor: {e}")
        self.cursor_rect = self.custom_cursor.get_rect() if self.custom_cursor else None

        # Initialize question manager
        from src.dataGen import QuestionManager
        self.q_manager = QuestionManager()
        
        hallway_path = os.path.join(BASE_DIR, "assets", "backgrounds", "hallway.png")
        try:
            h_img = pygame.image.load(hallway_path).convert()
            scale = SCREEN_HEIGHT / h_img.get_height()
            self.hallway_tex = pygame.transform.scale(h_img, (int(h_img.get_width() * scale), SCREEN_HEIGHT))
        except:
            self.hallway_tex = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.hallway_tex.fill((30, 30, 35))

        # 2. ADD THE SLICING CODE HERE:
        self.hallway_w = self.hallway_tex.get_width()
        self.mid_point = self.hallway_w // 2

        # Slicing the texture into the "Entrance" and the "Looping Hall"
        self.hallway_start = self.hallway_tex.subsurface((0, 0, self.mid_point, SCREEN_HEIGHT))
        self.hallway_loop = self.hallway_tex.subsurface((self.mid_point, 0, self.mid_point, SCREEN_HEIGHT))
        self.loop_w = self.hallway_loop.get_width()        

        self.background_assets = {}
        bg_names = ["title", "lost_sridhar", "lost_maiti", "lost_dioch", "class", "win_kris", "win_shri", "win_ken", "end"]
        for name in bg_names:
            path = os.path.join(BASE_DIR, "assets", "backgrounds", f"{name}.png")
            try:
                img = pygame.image.load(path).convert()
                self.background_assets[name] = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except:
                # Fallback if image is missing
                fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fallback.fill(BLACK)
                self.background_assets[name] = fallback

        # Load Battle Backgrounds
        self.battle_backgrounds = []
        try:
            for i in range(1, 4):  # For 3 professors
                bg_path = os.path.join(BASE_DIR, "assets", "backgrounds", f"battle_bg_{i}.png")
                bg = pygame.image.load(bg_path).convert()
                # Get original dimensions
                orig_w, orig_h = bg.get_size()
                # Calculate scale to cover screen while maintaining aspect ratio
                scale = max(SCREEN_WIDTH / orig_w, SCREEN_HEIGHT / orig_h)
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                bg = pygame.transform.smoothscale(bg, (new_w, new_h))
                # Center the image
                x_offset = (SCREEN_WIDTH - new_w) // 2
                y_offset = (SCREEN_HEIGHT - new_h) // 2
                # Create a surface the size of the screen
                final_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                final_bg.fill((0, 0, 0))  # Fill with black for any gaps
                final_bg.blit(bg, (x_offset, y_offset))
                bg = final_bg
                self.battle_backgrounds.append(bg)
        except Exception as e:
            print(f"Error loading battle backgrounds: {e}")
            # Create fallback backgrounds with different colors
            self.battle_backgrounds = [
                pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)),
                pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)),
                pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            ]
            self.battle_backgrounds[0].fill((40, 30, 50))   # Dark purple for level 1
            self.battle_backgrounds[1].fill((30, 40, 60))   # Dark blue for level 2
            self.battle_backgrounds[2].fill((50, 30, 30))   # Dark red for level 3


        self.state = MENU
        self.last_music_state = None  # Track which state's music is currently playing
        self.show_how_to_play = False
        self.selected_idx = None
        self.current_level = 0

        self.floor_h = int(SCREEN_HEIGHT * 0.20)   # replaces the hardcoded 200
        self.floor_y = SCREEN_HEIGHT - self.floor_h

        self.show_exit_prompt = False

        self.victory_timer = 0
        self.victory_stage = 0 
        self.is_player_victory = True
        # Initialize buttons as None to prevent AttributeErrors
        self.btn_start = None
        self.btn_help = None
        self.btn_quit = None
        self.btn_confirm = None
        self.btn_atk = None
        self.btn_heal = None
        self.answer_btns = []
        
        self.setup_data()
        self.load_questions()
        
        self.player = None
        self.boss = None
        self.battle_log = ""
        self.show_question = False
        self.current_q = None

        self.combat_text = ""
        self.combat_text_timer = 0
        self.combat_text_y_offset = 0

        # Screen fade transition
        self.fading = False
        self.fade_alpha = 0
        self.fade_speed = 12
        self.fade_direction = 1   # 1 = fade to black, -1 = fade from black
        self.next_state = None

        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill(BLACK)

        # Boss entrance animation
        self.boss_entering = False
        self.boss_x = SCREEN_WIDTH + int(SCREEN_WIDTH * 0.1)
        self.boss_target_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.30)
        self.boss_walk_speed = int(SCREEN_WIDTH * 0.003)


        # Hallway Variables
        self.player_world_x = int(SCREEN_WIDTH * 0.2)

        self.hallway_width = SCREEN_WIDTH * 4  # Make it MUCH longer (was * 2)
        self.camera_x = 0
        self.selected_door = None

        self.door_w = int(SCREEN_WIDTH * 0.15)
        self.door_h = int(SCREEN_HEIGHT * 0.38)
        self.door_interact_dist = int(SCREEN_WIDTH * 0.05)
        self.door_y = self.floor_y - self.door_h
        # Define 3 Door locations - SPREAD THEM OUT MORE

        door_positions = [0.1, 0.2, 0.3]
        self.door_locations = [
            {"x": int(self.hallway_width * p), "level": i, "rect": None}
            for i, p in enumerate(door_positions)
        ]
        # Track which doors the player was previously near (for sound playback on re-entry)
        self.doors_previously_near = set()
        
        # Load Door Assets
        try:
            self.door_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "door.png")).convert_alpha()
            self.door_upclose_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "door_cracked.png")).convert_alpha()
            # Scale them appropriately
            self.door_nametage_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "door_upclose.png")).convert_alpha()
            self.door_nametage_img = pygame.transform.scale(self.door_nametage_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.door_img = pygame.transform.scale(self.door_img, (self.door_w, self.door_h))
            self.door_upclose_img = pygame.transform.scale(self.door_upclose_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # Fallback if images don't exist yet
            self.door_img = pygame.Surface((200, 350))
            self.door_img.fill(GOLD)
            self.door_upclose_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.door_upclose_img.fill(GRAY)

    def draw_transparent_rect(self, surface, color, rect, alpha):
        s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        r, g, b = color
        s.fill((r, g, b, alpha))
        surface.blit(s, (rect.x, rect.y))
    def setup_data(self):
        self.roster = [
            Student(
                "Cs Get Degrees", 100, 15,
                "Hidden Ability: 25% chance to ignore a wrong answer on a dodge.",
                "C's Really Do Get Degrees! You passed!",
                sprite_folder=os.path.join(SPRITE_DIR, "swi", "standard", "idle", "right"),
                idle_frames=2
            ),
            Student(
                "4.0 Medallion", 100, 20,
                "Special: 20% Critical Hit chance (The Curve) for 1.5x damage.",
                "Academic Excellence!",
                sprite_folder=os.path.join(SPRITE_DIR, "kris", "standard", "idle", "right"),
                idle_frames=2,
            ),
            Student(
                "TA God", 100, 18,
                "Special: Healing restores twice as much HP (Lab Snacks).",
                "The lab is yours now!",
                sprite_folder=os.path.join(SPRITE_DIR, "ken", "standard", "idle", "right"),
                idle_frames=2,
            )
        ]
        self.roster[0].hover_path = os.path.join(SPRITE_DIR, "swi", "standard", "thrust", "left", "3.png")
        self.roster[1].hover_path = os.path.join(SPRITE_DIR, "kris", "standard", "thrust", "left", "3.png")
        self.roster[2].hover_path = os.path.join(SPRITE_DIR, "ken", "standard", "thrust", "left", "3.png")
        for s in self.roster:
            try:
                img = pygame.image.load(s.hover_path).convert_alpha()
                s.hover_sprite = img
            except:
                s.hover_sprite = None
        self.profs = [
            Professor(
                "Prof Sridhar", 150, 35,
                "Logic is not O(1). You fail Data Structures.",
                "The Biz",
                bossId=1,
                sprite_folder=os.path.join(SPRITE_DIR, "sridhar", "standard", "idle", "left"),
                idle_frames=2
            ),
            Professor(
                "Prof Diochnos", 200, 35,
                "This language is not decidable… and neither are you. You fail Theory.”",
                "Turing Machine Terrace",
                bossId=2,
                sprite_folder=os.path.join(SPRITE_DIR, "dioch", "standard", "idle", "left"),
                idle_frames=2
            ),
            Professor(
                "Prof Maiti", 275, 35,
                "Your hash has collisions. You fail Cryptography.",
                "Bitcoin Boulevard",
                bossId=3,
                sprite_folder=os.path.join(SPRITE_DIR, "maiti", "standard", "idle", "left"),
                idle_frames=2
            )
        ]


    def load_questions(self):
        self.q_manager = QuestionManager()  # Re-initialize to load questions into the manager



    # main.py

    def draw_hallway(self):
        start_screen_x = 0 - self.camera_x
        if start_screen_x < SCREEN_WIDTH:
            self.screen.blit(self.hallway_start, (start_screen_x, 0))

        # 2. Draw the repeating Second Half
        # We start drawing loops immediately after the mid_point
        # Calculate where the first loop tile should begin relative to camera
        first_loop_world_x = self.mid_point
        
        # Determine the offset for the repeating pattern
        # This ensures the loop starts exactly where the first half ends
        if self.camera_x < self.mid_point:
            # We can still see the transition point
            current_x = self.mid_point - self.camera_x
        else:
            # We are past the first half, calculate the tiling offset
            offset = (self.camera_x - self.mid_point) % self.loop_w
            current_x = -offset

        # Tile the loop until the screen is filled
        while current_x < SCREEN_WIDTH:
            self.screen.blit(self.hallway_loop, (current_x, 0))
            current_x += self.loop_w
        
        # 1. DRAW FLOOR (Relative to camera)
        # This creates a floor that spans the whole hallway width
      
        
        # 2. DRAW DOORS
        # Track which doors are currently near
        doors_currently_near = set()
        
        for i, door in enumerate(self.door_locations):
            screen_x = door["x"] - self.camera_x
            
            if -200 < screen_x < SCREEN_WIDTH:
                # CHECK PROXIMITY: If player is within 100 pixels of the door
                distance = abs(self.player_world_x - door["x"])
                is_near = distance < int(SCREEN_WIDTH * 0.05)
                is_unlocked = i <= self.current_level
                
                # Track this door as currently near
                if is_near and is_unlocked:
                    doors_currently_near.add(i)
                
                # Play door opening sound when player TRANSITIONS from not-near to near (wasn't near before, is now)
                if is_near and is_unlocked and i not in self.doors_previously_near:
                    door_sound_path = os.path.join(SFX_DIR, "dragon-studio-opening-door-sfx-454240.mp3")
                    self.sound.play_sfx(door_sound_path, volume=0.5)
                
                # Choose image based on proximity
                # door_upclose_img is actually your "cracked" version here
                if is_near and is_unlocked:
                    img_to_use = self.door_upclose_img
                else:
                    img_to_use = self.door_img
                
                # If it's the cracked version, we need to scale it down for the hallway view
                if is_near:
                    door_w = self.door_w
                    door_h = self.door_h
                    display_img = pygame.transform.scale(img_to_use, (door_w, door_h))
                else:
                    display_img = img_to_use

                # Darken if locked
                if i > self.current_level:
                    display_img = display_img.copy()
                    display_img.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_MULT)
                
                door_y = self.door_y
                self.screen.blit(display_img, (screen_x, door_y))
                door["rect"] = pygame.Rect(screen_x, door_y, self.door_w, self.door_h)

        # Update tracking for next frame
        self.doors_previously_near = doors_currently_near

        # trying to fix the Cs Get Degrees error
        player_draw_x = self.player_screen_x - int(SCREEN_WIDTH * 0.04)
        player_draw_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.50)
        self.player.update_animation()  # Update animation
        self.draw_character_with_shadow(self.player, player_draw_x, player_draw_y)
        if self.show_exit_prompt:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            draw_text(self.screen, "Return to Menu?", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70, self.title_font, WHITE, True)
            
            btn_w = int(SCREEN_WIDTH * 0.07)
            btn_h = int(SCREEN_HEIGHT * 0.07)
            gap = int(SCREEN_WIDTH * 0.02)

            total_w = btn_w * 2 + gap
            start_x = SCREEN_WIDTH//2 - total_w//2
            btn_y = SCREEN_HEIGHT//2 + int(SCREEN_HEIGHT * 0.05)

            self.btn_exit_yes = Button("YES", start_x, btn_y, btn_w, btn_h, OU_CREAM)
            self.btn_exit_no  = Button("NO",  start_x + btn_w + gap, btn_y, btn_w, btn_h, OU_CREAM)

            
            self.btn_exit_yes.draw(self.screen, self.font)
            self.btn_exit_no.draw(self.screen, self.font)
    

    def draw_door_view(self):
        self.screen.blit(self.door_nametage_img, (0, 0))
        # Details
        boss = self.profs[self.selected_door["level"]]

        title_text = f"OFFICE OF\n{boss.name.upper()}"
        lines = title_text.split('\n')
        current_y = 350
        line_spacing = self.title_font.get_linesize() 

        for line in lines:
            draw_text(self.screen, line, SCREEN_WIDTH//2, current_y, self.title_font, BLACK, True)
            current_y += line_spacing # Move the next line down
        draw_text(self.screen, boss.level_name, SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.53, self.font, BLACK, center=True)

        self.btn_confirm = Button("CHALLENGE", SCREEN_WIDTH//2 - 210, SCREEN_HEIGHT - 150, 200, 60, OU_CREAM)
        self.btn_back = Button("BACK", SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT - 150, 200, 60, OU_CREAM)
        
        self.btn_confirm.draw(self.screen, self.font)
        self.btn_back.draw(self.screen, self.font)

    def update_hallway(self):
        if self.victory_stage > 0:
            self.player.update() 
            return
        if not self.show_exit_prompt:
            keys = pygame.key.get_pressed()
            speed = 10
            if keys[pygame.K_e]:
                for i, door in enumerate(self.door_locations):
                    distance = abs(self.player_world_x - door["x"])
                    is_near = distance < self.door_interact_dist
                    is_unlocked = door["level"] <= self.current_level
                    if is_near and is_unlocked:
                        self.selected_door = door
                        self.state = DOOR_VIEW
                    # self.start_fade(DOOR_VIEW)
                        break
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player_world_x -= speed
                self.player.facing = "left"
                self.player.set_state(WALK)
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player_world_x += speed
                self.player.facing = "right"
                self.player.set_state(WALK)
            else:
                self.player.set_state(IDLE)
        else:
            self.player.set_state(IDLE)

        # FIX: Boundaries. 100 is the start, hallway_width is the end.
        # This prevents the "walking into darkness" issue.
        max_world_x = self.door_locations[-1]["x"] + 300
        self.player_world_x = max(100, min(self.player_world_x, max_world_x))
        
        target_camera_x = self.player_world_x - (SCREEN_WIDTH // 2)

        # Camera centering logic
        self.camera_x = max(0, min(target_camera_x, self.hallway_width - SCREEN_WIDTH))
        max_screen_x = SCREEN_WIDTH - 200

        player_screen_x = self.player_world_x - self.camera_x
        self.player_screen_x = player_screen_x
        if self.player_world_x <= 100:
            self.show_exit_prompt = True
        
        self.player.update()
        
    def reset_game(self):
        """Reset game state variables when returning to menu"""
        self.current_level = 0
        self.show_exit_prompt = False
        self.selected_idx = None
        self.player_world_x = int(SCREEN_WIDTH * 0.2)
        self.camera_x = 0
        self.player = None
        self.boss = None
        self.show_question = False
        self.current_q = None
        self.battle_log = ""
        self.combat_text = ""
        self.combat_text_timer = 0
        self.victory_stage = 0
        self.boss_entering = False
        self.selected_door = None
        self.doors_previously_near = set()  # Reset door tracking when returning to menu

    def start_fade(self, next_state):

        self.fading = True
        self.fade_direction = 1
        self.fade_alpha = 0
        self.next_state = next_state

    def handle_fade(self):
        if not self.fading:
            return

        self.fade_alpha += self.fade_speed * self.fade_direction

        # reached full black → switch state → fade back in
        if self.fade_alpha >= 255:
            self.fade_alpha = 255
            # Reset game state when transitioning to MENU
            if self.next_state == MENU:
                self.reset_game()
            self.state = self.next_state
            self.fade_direction = -1

        # finished fading back in
        elif self.fade_alpha <= 0:
            self.fade_alpha = 0
            self.fading = False

        self.fade_surface.set_alpha(self.fade_alpha)
        self.screen.blit(self.fade_surface, (0, 0))


    def draw_menu(self):
        intro_file = os.path.join(SFX_DIR, f"title_screen.wav")
        self.screen.blit(self.background_assets["title"], (0, 0))
        # Only initialize music if we just entered the MENU state
        if self.last_music_state != MENU:
            self.sound.clear_music()
            self.sound.play_music(intro_file)
            self.last_music_state = MENU
        
        side_margin = 0.025 * SCREEN_WIDTH

        help_w = 0.026 * SCREEN_WIDTH
        quit_w = 0.063 * SCREEN_WIDTH

        help_x = side_margin
        quit_x = SCREEN_WIDTH - side_margin - quit_w

        self.btn_start = Button("ENTER THE LAB", SCREEN_WIDTH//2 - int(SCREEN_WIDTH * 0.08), SCREEN_HEIGHT//2 + int(SCREEN_HEIGHT * 0.07), int(SCREEN_WIDTH * 0.16), int(SCREEN_HEIGHT * 0.06), OU_CREAM)
        self.btn_help = Button(
            "?",
            int(help_x),
            SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.08),
            int(help_w),
            int(SCREEN_HEIGHT * 0.05),
            OU_CREAM
        )

        self.btn_quit = Button(
            "QUIT",
            int(quit_x),
            SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.08),
            int(quit_w),
            int(SCREEN_HEIGHT * 0.05),
            OU_CREAM
        )

        
        self.btn_start.draw(self.screen, self.font)
        self.btn_help.draw(self.screen, self.font)
        self.btn_quit.draw(self.screen, self.font)

        if self.show_how_to_play:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            self.screen.blit(overlay, (0,0))
            
            # Draw scroll background
            scroll_x = SCREEN_WIDTH//2 - self.scroll_bg.get_width()//2
            scroll_y = SCREEN_HEIGHT//4
            self.screen.blit(self.scroll_bg, (scroll_x, scroll_y))
            
            draw_text(self.screen, "SYLLABUS (HOW TO PLAY)", SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + int(SCREEN_HEIGHT * 0.13), self.font, BLACK, True)
            instructions = [
                "1. Pick your Student character.",
                "2. Attack to lower the Professor's HP.",
                "3. Heal when low (but you can't heal at 100%!).",
                "4. When the Prof attacks, answer correctly to DODGE!",
                "5. Defeat all 3 professors to graduate.",
                "6. Walk left of the main hall to exit the game."
            ]
            for i, line in enumerate(instructions):
                draw_text(self.screen, line, SCREEN_WIDTH//5 + int(SCREEN_WIDTH * 0.02), SCREEN_HEIGHT//4 + int(SCREEN_HEIGHT * 0.2) + (i * int(SCREEN_HEIGHT * 0.04)), self.font, BLACK)
            draw_text(self.screen, "(Click anywhere to close)", SCREEN_WIDTH//2, SCREEN_HEIGHT*0.7, self.font, BLACK, True)

    def draw_loss(self):
        # Determine which lose screen to show
        if self.boss.bossId == 1:
            bg = self.background_assets["lost_sridhar"]
        elif self.boss.bossId == 2:
            bg = self.background_assets["lost_dioch"] # Dioch uses Maiti's
        else:
            bg = self.background_assets["lost_maiti"]
            
        self.screen.blit(bg, (0, 0))
        
        # Add a dark overlay to make text readable
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        draw_text(self.screen, self.boss.loss_msg, SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.9, self.font, OU_CRIMSON, True)
    def draw_character_preview(self, student, rect, facing="front"):
        frame = None
        if hasattr(student, "all_frames"):
            frames = student.all_frames.get(facing, {}).get(IDLE, [])
            if frames:
                frame = frames[0]

        if not frame:
            pygame.draw.rect(self.screen, BLACK, rect, border_radius=10)
            return

        padding = int(min(rect.w, rect.h) * 0.08)
        max_w = rect.w - padding * 2
        max_h = rect.h - padding * 2
        if max_w <= 0 or max_h <= 0:
            return

        frame_w, frame_h = frame.get_size()
        scale = min(max_w / frame_w, max_h / frame_h)
        target_w = max(1, int(frame_w * scale))
        target_h = max(1, int(frame_h * scale))

        sprite = pygame.transform.smoothscale(frame, (target_w, target_h))
        draw_x = rect.x + (rect.w - target_w) // 2
        draw_y = rect.y + (rect.h - target_h) // 2
        self.screen.blit(sprite, (draw_x, draw_y))

    def draw_character_select(self):
        self.screen.blit(self.background_assets["class"], (0, 0))
        
        # Continue menu music or initialize SELECT music if it changes
        if self.last_music_state != SELECT:
            # Keep playing the same intro music during character selection
            # (or use a different track here if desired, e.g., os.path.join(SFX_DIR, f"select_screen.wav"))
            self.last_music_state = SELECT
        
        title = "CHOOSE YOUR STUDENT"
        tx = SCREEN_WIDTH // 2
        ty = int(SCREEN_HEIGHT * 0.2)
        card_w, card_h = int(SCREEN_WIDTH * 0.18), int(SCREEN_HEIGHT * 0.45)
        gap = (SCREEN_WIDTH - (3 * card_w)) // 4
        m_pos = pygame.mouse.get_pos()

        # Outline (black)
        for ox, oy in [(-3,0),(3,0),(0,-3),(0,3)]:
            draw_text(self.screen, title, tx + ox, ty + oy, self.title_font, BLACK, True)

        # Main text (cream)
        draw_text(self.screen, title, tx, ty, self.title_font, OU_CREAM, True)
        # Determine hovered card index
        hover_idx = None
        for i in range(len(self.roster)):
            x = gap + i * (card_w + gap)
            y = int(SCREEN_HEIGHT * 0.35)
            rect = pygame.Rect(x, y, card_w, card_h)
            if rect.collidepoint(m_pos):
                hover_idx = i
                break

        self.selected_idx = hover_idx
        if self.selected_idx is None:
            # NO ONE HOVERED: Show 3 normal cards in IDLE
            for i, s in enumerate(self.roster):
                x = gap + i * (card_w + gap)
                y = int(SCREEN_HEIGHT * 0.35)
                rect = pygame.Rect(x, y, card_w, card_h)
                
                self.draw_transparent_rect(self.screen, GRAY, rect, 180)
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=15)

                # Define preview_rect inside the loop so it knows the current x/y
                preview_rect = pygame.Rect(x + int(card_w * 0.14), y + int(card_h * 0.09), int(card_w * 0.71), int(card_h * 0.54))
                
                # Default to Idle since nothing is hovered in this block
                self.draw_character_preview(s, preview_rect)
                draw_text(self.screen, s.name, x + card_w//2, y + int(card_h * 0.68), self.font, WHITE, True)
        
        else:
            # SOMEONE IS HOVERED: Enlarge focused, keep others small
            s_focused = self.roster[self.selected_idx]
            large_w, large_h = int(SCREEN_WIDTH * 0.23), int(SCREEN_HEIGHT * 0.58)

            for i, other in enumerate(self.roster):
                x = gap + i * (card_w + gap)
                y = int(SCREEN_HEIGHT * 0.35)
                rect = pygame.Rect(x, y, card_w, card_h)

                if i == self.selected_idx:
                    # DRAW THE ENLARGED FOCUSED CARD
                    fx = x - (large_w - card_w) // 2
                    fy = y - (large_h - card_h) // 2
                    f_rect = pygame.Rect(fx, fy, large_w, large_h)
                    
                    pygame.draw.rect(self.screen, GOLD, f_rect, border_radius=15)
                    pygame.draw.rect(self.screen, WHITE, f_rect, 4, border_radius=15)

                    p_rect = pygame.Rect(fx + int(large_w * 0.11), fy + int(large_h * 0.07), int(large_w * 0.78), int(large_h * 0.54))
                    
                    # THRUST SPRITE FOR FOCUSED
                    if hasattr(s_focused, 'hover_sprite') and s_focused.hover_sprite:
                        img = s_focused.hover_sprite
                        scale = min(p_rect.w / img.get_width(), p_rect.h / img.get_height())
                        scaled = pygame.transform.smoothscale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                        self.screen.blit(scaled, (p_rect.centerx - scaled.get_width()//2, p_rect.centery - scaled.get_height()//2))
                    else:
                        self.draw_character_preview(s_focused, p_rect)

                    # Text for Focused Card
                    draw_text(self.screen, s_focused.name, fx + large_w//2, fy + int(large_h * 0.62), self.medium_font, BLACK, True)
                    self.small_font.set_bold(True)
                    draw_text(self.screen, "SPECIAL ABILITY:", fx + large_w//2, fy + int(large_h * 0.70), self.small_font, GOLD, True)
                    lines = wrap_text(s_focused.ability_desc, self.small_font, int(large_w * 0.82))
                    for j, line in enumerate(lines):
                        draw_text(self.screen, line, fx + large_w//2, fy + int(large_h * 0.75) + (j * 20), self.small_font, BLACK, True)
                    self.small_font.set_bold(False)
                
                else:
                    # DRAW OTHER SMALL CARDS (Idle)
                    self.draw_transparent_rect(self.screen, GRAY, rect, 180)
                    pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=15)
                    p_rect = pygame.Rect(x + int(card_w * 0.14), y + int(card_h * 0.09), int(card_w * 0.71), int(card_h * 0.54))
                    self.draw_character_preview(other, p_rect)
                    draw_text(self.screen, other.name, x + card_w//2, y + int(card_h * 0.68), self.font, WHITE, True)
    def show_combat_text(self, text, color=GRAY):
        self.combat_text = text
        self.combat_text_color = color
        self.combat_text_timer = pygame.time.get_ticks() + 2000
        self.combat_text_y_offset = -30

    def draw_character_with_shadow(self, character, x, y):
        # Shadow offset and color
        shadow_offset = 5
        shadow_color = (0, 0, 0, 150)  # Semi-transparent black
        
        # Get the current frame to draw
        if character.override_frames:
            if character.override_index >= len(character.override_frames):
                character.override_index = len(character.override_frames) - 1
            frame = character.override_frames[character.override_index]
        else:
            current_dir_frames = character.all_frames[character.facing]
            current_frames = current_dir_frames.get(character.state, current_dir_frames[IDLE])
            
            if not current_frames or character.current_frame >= len(current_frames):
                character.current_frame = 0
                if not current_frames:
                    current_frames = current_dir_frames[IDLE]
            
            if len(current_frames) == 0:
                return  # Can't draw without frames
            
            frame = current_frames[character.current_frame]
        
        # Create shadow surface
        shadow = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))  # Transparent
        
        # Draw shadow in 8 directions (or 4 for simpler shadow)
        for dx, dy in [(-shadow_offset, 0), (shadow_offset, 0), 
                    (0, -shadow_offset), (0, shadow_offset),
                    (-shadow_offset, -shadow_offset), (shadow_offset, shadow_offset),
                    (-shadow_offset, shadow_offset), (shadow_offset, -shadow_offset)]:
            shadow.blit(frame, (0, 0))
            # Apply shadow color with alpha
            shadow.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(shadow, (x + dx, y + dy))
        
        # Draw the actual character on top
        self.screen.blit(frame, (x, y))
    def draw_total_win(self):
        # 1. Background
        self.screen.blit(self.background_assets["end"], (0, 0))
        
        # 2. OU_CREAM Header Box
        header_w, header_h = int(SCREEN_WIDTH * 0.5), 80
        header_rect = pygame.Rect(SCREEN_WIDTH//2 - header_w//2, 40, header_w, header_h)
        
        # Draw semi-transparent background for the box
        s = pygame.Surface((header_w, header_h), pygame.SRCALPHA)
        # Using OU_CREAM with 220 alpha for a solid yet soft look
        s.fill((249, 244, 227, 220)) 
        self.screen.blit(s, (header_rect.x, header_rect.y))
        
        # Border for the box
        pygame.draw.rect(self.screen, BLACK, header_rect, 3, border_radius=5)
        
        # Congrats Text inside the box
        draw_text(self.screen, "DEGREE CONFERRED: C.S. COMPLETED!", 
                  SCREEN_WIDTH//2, 69, self.medium_font, BLACK, True)

        # 3. Exit Button
        btn_w, btn_h = 300, 60
        self.btn_exit_win = Button("RETURN TO TITLE", 
                                    SCREEN_WIDTH//2 - btn_w//2, 
                                    SCREEN_HEIGHT - 100, 
                                    btn_w, btn_h, OU_CREAM)
        self.btn_exit_win.draw(self.screen, self.font)
    def draw_battle(self):
        boss_music_id = self.boss.bossId  # the boss for this level
        if getattr(self, 'current_boss_music_id', None) != boss_music_id:
            # Boss has changed, start new music
            self.sound.clear_music()
            self.sound.play_music(os.path.join(SFX_DIR, f"Boss{boss_music_id}_music.wav"), volume=0.1)
            self.current_boss_music_id = boss_music_id
    
        bg_index = self.boss.bossId - 1  # Convert boss ID (1,2,3) to index (0,1,2)
        if 0 <= bg_index < len(self.battle_backgrounds):
            self.screen.blit(self.battle_backgrounds[bg_index], (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  # Adjust the last value (0-255) for darkness
            self.screen.blit(overlay, (0, 0))

        floor_height = int(SCREEN_HEIGHT * 0.3)
        floor_y = SCREEN_HEIGHT - floor_height
         # Box dimensions
        box_w, box_h = int(SCREEN_WIDTH * 0.225), int(SCREEN_HEIGHT * 0.09)
        padding = 15

        # Check for Low Health (30%)
        is_low_health = self.player and self.player.hp <= (self.player.max_hp * 0.3)
        
        for i, x_pos in enumerate([padding, SCREEN_WIDTH - box_w - padding]):
            # Default: See-through Black
            bg_color = (0, 0, 0, 160)
            draw_x, draw_y = x_pos, padding

            # If health is low AND this is the player's box (the first one in the loop)
            if is_low_health and i == 0:
                # Change to See-through Red
                bg_color = (200, 0, 0, 180)
                # Apply the Shake effect
                draw_x += random.randint(-5, 5)
                draw_y += random.randint(-5, 5)

            # Create the transparent surface
            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(box_surf, bg_color, (0, 0, box_w, box_h), border_radius=12)
            
            # Blit the box with the potential shake offset
            self.screen.blit(box_surf, (draw_x, draw_y))
        if self.boss.bossId == 1:
    # Level 1: Grass texture
            grass_path = os.path.join(BASE_DIR, "assets", "backgrounds", "grass.png")
            try:
                grass = pygame.image.load(grass_path).convert_alpha()
                grass = pygame.transform.scale(grass, (SCREEN_WIDTH, floor_height))
                self.screen.blit(grass, (0, floor_y + SCREEN_HEIGHT*0.03))
            except:
                # Fallback: green ground
                floor_surface = pygame.Surface((SCREEN_WIDTH, floor_height), pygame.SRCALPHA)
                floor_surface.fill((34, 139, 34, 200))  # Forest green
                self.screen.blit(floor_surface, (0, floor_y))
        elif self.boss.bossId == 2:
            navy_path = os.path.join(BASE_DIR, "assets", "backgrounds", "navy.png")
            try:
                navy = pygame.image.load(navy_path).convert_alpha()
                navy = pygame.transform.scale(navy, (SCREEN_WIDTH, floor_height))
                # FIX: Changed 'tile' to 'navy'
                self.screen.blit(navy, (0, floor_y + SCREEN_HEIGHT*0.03))
            except:
                # Fallback: Dark Navy
                floor_surface = pygame.Surface((SCREEN_WIDTH, floor_height), pygame.SRCALPHA)
                floor_surface.fill((0, 0, 128, 200))  # Dark Navy
                self.screen.blit(floor_surface, (0, floor_y))
        else:  # Level 3
            tile_path = os.path.join(BASE_DIR, "assets", "backgrounds", "tile.png")
            try:
                tile = pygame.image.load(tile_path).convert_alpha()
                tile = pygame.transform.scale(tile, (SCREEN_WIDTH, floor_height))
                self.screen.blit(tile, (0, floor_y + SCREEN_HEIGHT*0.03))
            except:
                # Fallback: Dark Purple
                floor_surface = pygame.Surface((SCREEN_WIDTH, floor_height), pygame.SRCALPHA)
                floor_surface.fill((48, 25, 52, 200))  # Dark Purple
                self.screen.blit(floor_surface, (0, floor_y))

        # Draw player with shadow
        player_x = int(SCREEN_WIDTH * 0.08)
        player_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.55)
        self.player.update_animation()  # Update animation
        self.draw_character_with_shadow(self.player, player_x, player_y)

        boss_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.63)

       
        # ----- Boss entrance walking -----
        if self.boss_entering:
            self.boss.set_state(WALK)
            self.boss_x -= self.boss_walk_speed
            if self.boss_x <= self.boss_target_x:
                self.boss_x = self.boss_target_x
                self.boss_entering = False
                self.boss.set_state(IDLE)

        # Draw boss with shadow
        self.boss.update_animation()  # Update animation
        self.draw_character_with_shadow(self.boss, self.boss_x, boss_y)

        btn_width = int(SCREEN_WIDTH * 0.12)
        btn_height = int(SCREEN_HEIGHT * 0.055)
        btn_spacing = int(SCREEN_WIDTH * 0.015)
        btn_width = int(SCREEN_WIDTH * 0.16)
        btn_spacing = int(SCREEN_WIDTH * 0.015)
        btn_margin = int(SCREEN_WIDTH * 0.05)
        # UI Header
        player_hp_display = max(0, self.player.hp)  # clamp to 0
        p_hp_ratio = self.player.hp / self.player.max_hp
        b_hp_ratio = self.boss.hp / self.boss.max_hp
        hp_bar_w = int(SCREEN_WIDTH * 0.18)
        hp_bar_h = int(SCREEN_HEIGHT * 0.03)
        hp_y = int(SCREEN_HEIGHT * 0.05)
        text_y = int(SCREEN_HEIGHT * 0.02)

        # Player HP (left)
        ui_margin = int(SCREEN_WIDTH * 0.026)
        pygame.draw.rect(self.screen, OU_CRIMSON, (ui_margin, hp_y, hp_bar_w, hp_bar_h))
        pygame.draw.rect(self.screen, GREEN, (ui_margin, hp_y, hp_bar_w * p_hp_ratio, hp_bar_h))
        draw_text(self.screen, f"{self.player.name}: {player_hp_display} HP", ui_margin, text_y, self.font)

        # Boss HP (right, mirrored)
        boss_hp_display = max(0, self.boss.hp)  # clamp to 0

        boss_bar_x = SCREEN_WIDTH - ui_margin - hp_bar_w
        pygame.draw.rect(self.screen, OU_CRIMSON, (boss_bar_x, hp_y, hp_bar_w, hp_bar_h))
        pygame.draw.rect(self.screen, GREEN, (boss_bar_x, hp_y, hp_bar_w * b_hp_ratio, hp_bar_h))
        boss_text = f"{self.boss.name}: {boss_hp_display} HP"
        text_surface = self.font.render(boss_text, True, WHITE)
        text_x = SCREEN_WIDTH - ui_margin - text_surface.get_width()
        self.screen.blit(text_surface, (text_x, text_y))



        # Control Box
        ui_rect = pygame.Rect(ui_margin,
            SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.18),
            SCREEN_WIDTH - ui_margin*2,
            int(SCREEN_HEIGHT * 0.15))
        
        pygame.draw.rect(self.screen, BLACK, ui_rect.inflate(0, 10), border_radius=15)
        pygame.draw.rect(self.screen, OU_CRIMSON, ui_rect, 4, border_radius=15)

     
        if self.combat_text and pygame.time.get_ticks() < self.combat_text_timer:
            # float upward
            self.combat_text_y_offset -= 0.5
            
            # fade out
            time_left = self.combat_text_timer - pygame.time.get_ticks()
            alpha = max(0, min(255, int(255 * (time_left / 1000))))
            
            # BIG dramatic font
            big_font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.05), bold=True)
            lines = self.combat_text.split('\n')
            line_height = big_font.get_height()
            
            # Render each line with outline
            for i, line in enumerate(lines):
                text_x = ui_margin + int(SCREEN_WIDTH * 0.075)
                text_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.6) + self.combat_text_y_offset + (i * line_height)
                
                # Draw white outline (8 directions)
                for dx, dy in [(-2, -2), (0, -2), (2, -2),
                            (-2, 0),           (2, 0),
                            (-2, 2),  (0, 2),  (2, 2)]:
                    outline_surface = big_font.render(line, True, WHITE)
                    outline_surface.set_alpha(alpha)
                    self.screen.blit(outline_surface, (text_x + dx, text_y + dy))
                
                # Draw main text on top
                txt_surface = big_font.render(line, True, self.combat_text_color)
                txt_surface.set_alpha(alpha)
                self.screen.blit(txt_surface, (text_x, text_y))

        if self.show_question:
            draw_speech_bubble(
                self.screen,
                self.current_q['text'],
                SCREEN_WIDTH - int(SCREEN_WIDTH * 0.23),
                SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.60),
                self.font,
                type="boss"
            )
            self.answer_btns = []
            num_choices = len(self.current_q['choices'])
            
            total_width = (num_choices * btn_width) + ((num_choices - 1) * btn_spacing)
            start_x = (SCREEN_WIDTH - total_width) / 2

            for i, opt in enumerate(self.current_q['choices']):
                x = start_x + (i * (btn_width + btn_spacing))
                btn = Button(opt, int(x), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.11), btn_width, int(SCREEN_HEIGHT * 0.12), OU_CREAM)
                btn.draw(self.screen, self.font)
                self.answer_btns.append(btn)
        else:
            text_margin = int(SCREEN_WIDTH * 0.05)  # 5% of screen width from the left edge
            draw_text(
                self.screen,
                self.battle_log,
                text_margin,
                SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.12),
                self.font
            )
            current_time = pygame.time.get_ticks()
            heal_disabled = (self.player.numHeals <= 0) or (self.player.hp >= self.player.max_hp)
            is_locked = (current_time - getattr(self, 'battle_start_time', 0)) < 4500
            atk_color = (128, 128, 128) if is_locked else GOLD
            self.btn_atk = Button(
                "ATTACK",
                SCREEN_WIDTH - btn_margin - 2*btn_width - btn_spacing,
                SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.105),
                btn_width,
                btn_height,
                (255, 0, 0),
                atk_color,
                disabled=is_locked
            )

            self.btn_heal = Button(
                "HEAL",
                SCREEN_WIDTH - btn_margin - btn_width,
                SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.105),
                btn_width,
                btn_height,
                GREEN,
                disabled=heal_disabled
            )
            self.btn_atk.draw(self.screen, self.font)
            self.btn_heal.draw(self.screen, self.font)

    
        if self.victory_stage > 0:
            elapsed = pygame.time.get_ticks() - self.victory_timer
            
            if self.victory_stage == 1 and elapsed > 2000:  # Changed from 600 - almost immediate
                self.victory_stage = 2
                self.victory_timer = pygame.time.get_ticks()
            
            elif self.victory_stage == 2 and elapsed > 100:  # Changed from 3000 - just enough to see pose
                self.victory_stage = 3  # NEW stage - holding pose during fade
                
                # Fade to appropriate state based on outcome
                if self.is_player_victory:
                    self.start_fade(WIN)
                    self.boss_entering = True
                    self.boss_x = SCREEN_WIDTH + 200
                else:
                    self.start_fade(LOSS)
        # Check if health is low
        
        if self.flash_timer > 0:
            # Create a white surface the size of the screen
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill(WHITE)
            # Set a high transparency (alpha)
            flash_surf.set_alpha(100) 
            self.screen.blit(flash_surf, (0,0))
            self.flash_timer -= 1


    def handle_battle_click(self, mouse_pos):
        if self.boss_entering or self.victory_stage > 0:
            return

        if not self.show_question:
            if self.btn_atk and self.btn_atk.is_clicked(mouse_pos):
                dmg, msg, is_special = self.player.calculate_attack()
                if is_special:
                    self.sound.play_sfx(os.path.join(SFX_DIR, "critical_hit.wav"), volume=0.1)
                else:
                    self.sound.play_sfx(os.path.join(SFX_DIR, "punch_sound.wav"), volume=0.1)
                self.show_combat_text(msg, GOLD if is_special else GRAY)

                self.boss.hp -= dmg
                self.flash_timer = 5
                self.player.play_animation("slash", "right", 6)
                self.boss.play_animation("hurt", "up", 3)


                
                self.battle_log = f"You dealt {dmg} damage!"

                #or self.show_combat_text(msg) ## self.battle_log = f"You dealt {dmg} damage!"

                if self.boss.hp <= 0: 
                    self.boss.play_animation("hurt", "up", 5, freeze_last=True)
                    self.player.play_animation("spellcast", "right", 6, freeze_last=True)
                    self.victory_timer = pygame.time.get_ticks()
                    self.victory_stage = 1
                    self.is_player_victory = True
                    self.sound.clear_music()  # Clear music after 2 seconds to allow win sound to play
                    self.sound.play_voice(os.path.join(SFX_DIR, f"win-sound.wav"), volume=0.3)
                   # self.boss_entering = True
                   # self.boss_x = SCREEN_WIDTH + 200


                else:
                    # Pull a random question for this boss
                    self.show_question = True
                    self.current_q = self.q_manager.get_random_question(self.boss.bossId)
                    if self.boss.bossId == 2 or self.boss.bossId == 3:
                        self.sound.play_random_voiceline(self.boss.bossId, volume = 0.3)  # Play a random voiceline for the boss when they ask a question"
                    else:
                        self.sound.play_random_voiceline(self.boss.bossId, volume = 1.0)  # Play a random voiceline for the boss when they ask a question

            elif self.btn_heal and self.btn_heal.is_clicked(mouse_pos):
                amt, msg, is_special = self.player.get_heal_amount()
                self.show_combat_text(msg, GOLD if is_special else GRAY)

                self.player.hp = min(self.player.max_hp, self.player.hp + amt)
              #  self.player.say(msg) # Player says they healed

                
                self.show_question = True
                self.current_q = self.q_manager.get_random_question(self.boss.bossId)
                if self.boss.bossId == 2 or self.boss.bossId == 3:
                    self.sound.play_random_voiceline(self.boss.bossId, volume=0.3)  # Play a random voiceline for the boss when they ask a question
                else:
                    self.sound.play_random_voiceline(self.boss.bossId, volume=1)  # Play a random voiceline for the boss when they ask a question
                
                self.player.numHeals -= 1 # Decrease the number of heals left
                
        else:
            for btn in self.answer_btns:
                if btn.is_clicked(mouse_pos):
                    # Get the correct answer from the JSON
                    correct_index = self.current_q['correct']
                    correct_answer = self.current_q['choices'][correct_index]

                    if btn.text == correct_answer:
                        self.battle_log = "CORRECT! You dodged the grade deduction!"
                        self.show_combat_text("DODGED!", (0,255,255))
                        self.sound.play_sfx(os.path.join(SFX_DIR, "dodge.mp3"), volume=0.1)

                    else:
                        if self.player.name == "Cs Get Degrees" and random.random() < 0.25:
                            self.battle_log = "WRONG! But the curve saved you!"
                        else:
                            dmg = self.boss.attack_power
                            self.player.hp -= dmg
                            self.boss.play_animation("spellcast", "down", 6)
                            self.player.play_animation("hurt", "up", 3)

                            self.battle_log = f"INCORRECT! Lost {dmg} HP!"

                    # Done showing the question
                    self.show_question = False

                    # Check if the player lost all HP
                    if self.player.hp <= 0:
                        self.player.play_animation("hurt", "up", 5, freeze_last=True)
                        self.boss.play_animation("spellcast", "left", 6, freeze_last=True)
                        self.victory_timer = pygame.time.get_ticks()
                        self.victory_stage = 1
                        self.is_player_victory = False
                        self.sound.clear_music()  # Clear music after 2 seconds to allow win sound to play
                        self.sound.play_voice(os.path.join(SFX_DIR, f"lose_sound.wav"), volume=0.2)
    def transition_to_battle(self):
        self.battle_start_time = pygame.time.get_ticks()
        self.boss = self.profs[self.selected_door["level"]]
        self.start_fade(BATTLE)
        intro_file = os.path.join(AUDIO_DIR, f"Prof{self.boss.bossId}Intro.wav")
        if self.boss.bossId == 2 or self.boss.bossId == 3:
            self.sound.play_voice(intro_file, volume = 0.3)  # Play a random voiceline for the boss when they enter"
        else:
            self.sound.play_voice(intro_file)
        self.player.facing = "right"
        self.boss.facing = "left"
        self.boss.hp = self.boss.max_hp
        self.player.set_state(IDLE)
        self.boss.set_state(IDLE)

        self.boss.override_frames = None
        self.boss.override_index = 0
        self.boss.freeze_last_frame = False

        self.start_fade(BATTLE)
        self.boss_entering = True
        self.boss_x = SCREEN_WIDTH + 200
    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK)
            m_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p and self.state == BATTLE:
                    self.boss.hp = 0  # Instantly defeat the boss
                    self.boss.play_animation("hurt", "up", 5, freeze_last=True)
                    self.player.play_animation("spellcast", "right", 6, freeze_last=True)
                    self.victory_timer = pygame.time.get_ticks()
                    self.victory_stage = 1
                    self.is_player_victory = True
                    self.sound.clear_music()
                    self.sound.play_voice(os.path.join(SFX_DIR, f"win-sound.wav"), volume=0.3)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        # 1. Continue from Door View to Battle
                        if self.state == DOOR_VIEW:
                            # We trigger the same logic as the Confirm Button
                            self.transition_to_battle() 
                            
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_how_to_play:
                        self.show_how_to_play = False
                    elif self.state == MENU:
                        self.reset_game()
                        if self.btn_start and self.btn_start.is_clicked(m_pos): self.state = SELECT
                        if self.btn_help and self.btn_help.is_clicked(m_pos): self.show_how_to_play = True
                        if self.btn_quit and self.btn_quit.is_clicked(m_pos): running = False
                    elif self.state == SELECT:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            # If a character is currently hovered, clicking selects them and starts
                            if self.selected_idx is not None:
                                self.player = self.roster[self.selected_idx]
                                self.start_fade(HALLWAY)

                        
                    elif self.state == HALLWAY:
                        if self.show_exit_prompt:
                            if self.btn_exit_yes.is_clicked(m_pos):
                                self.show_exit_prompt = False
                                self.start_fade(MENU)
                            elif self.btn_exit_no.is_clicked(m_pos):
                                self.show_exit_prompt = False
                                self.player_world_x = 150  # Move them slightly away from edge
                        else:
                            for i, door in enumerate(self.door_locations):
                                # Check if door is clickable: must be unlocked AND player is near
                                distance = abs(self.player_world_x - door["x"])
                                is_near = distance < self.door_interact_dist
                                is_unlocked = door["level"] <= self.current_level
                                
                                if door["rect"] and door["rect"].collidepoint(m_pos) and is_unlocked and is_near:
                                    self.selected_door = door
                                    self.state = DOOR_VIEW
                    elif self.state == DOOR_VIEW:
                        if self.btn_confirm.is_clicked(m_pos):
                            self.transition_to_battle()
                        elif self.btn_back.is_clicked(m_pos):
                            self.state = HALLWAY
                    elif self.state == BATTLE:
                        self.handle_battle_click(m_pos)
                    
                    elif self.state in [WIN, LOSS]:
                        if self.state == WIN:
                            # 1. CHECK FOR TOTAL VICTORY FIRST
                            if self.current_level >= 2:
                                
                                self.start_fade(TOTAL_WIN)
                                # We skip everything else and go straight to graduation
                                continue 
                            
                            # 2. NORMAL LEVEL WIN
                            self.current_level += 1
                            self.battle_log = f"Level {self.current_level + 1} Unlocked!"
                        
                        else: # THIS IS THE LOSS CASE
                            self.battle_log = "Try again, student!"

                        # 3. SHARED RESET LOGIC (For normal wins and all losses)
                        self.player.hp = self.player.max_hp
                        self.player.override_frames = None
                        self.player.override_index = 0
                        self.player.set_state(IDLE)
                        
                        self.victory_stage = 0
                        self.boss_entering = True
                        self.show_question = False
                        
                        # Return to the hallway to try again or go to the next door
                        self.start_fade(HALLWAY)
                    elif self.state == TOTAL_WIN:
                        if hasattr(self, 'btn_exit_win') and self.btn_exit_win.is_clicked(m_pos):
                            self.reset_game()
                            self.start_fade(MENU)
            if self.state == MENU: self.draw_menu()
            elif self.state == SELECT: self.draw_character_select()
            elif self.state == HALLWAY: 
                self.update_hallway()
                self.draw_hallway()
            elif self.state == DOOR_VIEW: self.draw_door_view()
            elif self.state == BATTLE: self.draw_battle()
            elif self.state == WIN:
                win_bg = "title" # Default fallback
                if self.player:
                    if self.player.name == "4.0 Medallion":
                        win_bg = "win_kris"
                    elif self.player.name == "Cs Get Degrees":
                        win_bg = "win_shri"
                    elif self.player.name == "TA God":
                        win_bg = "win_ken"
                # Draw the specific background
                self.screen.blit(self.background_assets[win_bg], (0, 0))

                # Draw a subtle dark overlay to keep the text readable
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 80)) 
                self.screen.blit(overlay, (0, 0))

                # Draw the win messages
                #draw_text(self.screen, self.player.win_msg, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10, self.font, GREEN, True)
            elif self.state == TOTAL_WIN:
                self.draw_total_win()
                
            elif self.state == LOSS:
                self.draw_loss()
                self.player.hp = self.player.max_hp
                self.boss.hp = self.boss.max_hp

            self.handle_fade()
            
            # Draw custom cursor
            if self.custom_cursor:
                cursor_rect = self.custom_cursor.get_rect(topleft=m_pos)
                self.screen.blit(self.custom_cursor, cursor_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    Game().run() 