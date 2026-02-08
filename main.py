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

pygame.init()
pygame.mixer.init()  # This is required to play sounds

class Game:
    def __init__(self):
        self.sound = SoundManager()
        pygame.init()
        # Center the window on all platforms (Windows, macOS, Linux)
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        
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
        scroll_path = os.path.join(BASE_DIR, "assets", "backgrounds", "scroll.webp")
        self.scroll_bg = pygame.image.load(scroll_path)
        self.scroll_bg = pygame.transform.scale(self.scroll_bg, (int(SCREEN_WIDTH * 0.65), int(SCREEN_HEIGHT * 0.55)))
        
        # Initialize question manager
        from src.dataGen import QuestionManager
        self.q_manager = QuestionManager()
        
        self.state = MENU
        self.show_how_to_play = False
        self.selected_idx = None
        self.current_level = 0

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
        self.boss_target_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.23)
        self.boss_walk_speed = int(SCREEN_WIDTH * 0.003)


        # Hallway Variables
        self.player_world_x = 400
        self.hallway_width = SCREEN_WIDTH * 4  # Make it MUCH longer (was * 2)
        self.camera_x = 0
        self.selected_door = None

        # Define 3 Door locations - SPREAD THEM OUT MORE
        self.door_locations = [
            {"x": 600, "level": 0, "rect": None},      # Was 600
            {"x": 1200, "level": 1, "rect": None},     # Was 1200
            {"x": 1800, "level": 2, "rect": None}      # Was 1800
        ]
        
        # Load Door Assets
        try:
            self.door_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "door.png")).convert_alpha()
            self.door_upclose_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "door_cracked.png")).convert_alpha()
            # Scale them appropriately
            self.door_img = pygame.transform.scale(self.door_img, (200, 350))
            self.door_upclose_img = pygame.transform.scale(self.door_upclose_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # Fallback if images don't exist yet
            self.door_img = pygame.Surface((200, 350))
            self.door_img.fill(GOLD)
            self.door_upclose_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.door_upclose_img.fill(GRAY)



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
                scale = 4
            )
        ]
        
        self.profs = [
            Professor(
                "Prof Sridhar", 150, 35,
                "Logic is not O(1). You fail Data Structures.",
                "Top Floor Devon",
                bossId=1,
                sprite_folder=os.path.join(SPRITE_DIR, "sridhar", "standard", "idle", "left"),
                idle_frames=2
            ),
            Professor(
                "Prof Diochnos", 200, 35,
                "Model Underfitted. You fail ML.",
                "The Clouds",
                bossId=2,
                sprite_folder=os.path.join(SPRITE_DIR, "sridhar", "standard", "idle", "left"),
                idle_frames=2
            ),
            Professor(
                "Prof Maiti", 275, 35,
                "Compiling error... You fail Java 2.",
                "Library Lawn",
                bossId=3,
                sprite_folder=os.path.join(SPRITE_DIR, "sridhar", "standard", "idle", "left"),
                idle_frames=2
            )
        ]


    def load_questions(self):
        self.q_manager = QuestionManager()  # Re-initialize to load questions into the manager



    # main.py

    def draw_hallway(self):
        self.screen.fill((20, 20, 25))
        
        # 1. DRAW FLOOR (Relative to camera)
        # This creates a floor that spans the whole hallway width
        pygame.draw.rect(self.screen, (45, 45, 50), (-self.camera_x, SCREEN_HEIGHT - 200, self.hallway_width, 200))
        
        # 2. DRAW DOORS
        for i, door in enumerate(self.door_locations):
            screen_x = door["x"] - self.camera_x
            
            if -200 < screen_x < SCREEN_WIDTH:
                # CHECK PROXIMITY: If player is within 100 pixels of the door
                distance = abs(self.player_world_x - door["x"])
                is_near = distance < 100
             
                
                # Choose image based on proximity
                # door_upclose_img is actually your "cracked" version here
                if is_near and i <= self.current_level:
                    img_to_use = self.door_upclose_img
                else:
                    img_to_use = self.door_img
                
                # If it's the cracked version, we need to scale it down for the hallway view
                if is_near:
                    display_img = pygame.transform.scale(img_to_use, (200, 350))
                else:
                    display_img = img_to_use

                # Darken if locked
                if i > self.current_level:
                    display_img = display_img.copy()
                    display_img.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_MULT)
                
                self.screen.blit(display_img, (screen_x, SCREEN_HEIGHT - 550))
                door["rect"] = pygame.Rect(screen_x, SCREEN_HEIGHT - 550, 200, 350)

        # 3. DRAW PLAYER (Centered on screen)
        self.player.draw(self.screen, self.player_screen_x - 75, SCREEN_HEIGHT - 450)
        if self.show_exit_prompt:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            draw_text(self.screen, "Return to Menu?", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, self.title_font, WHITE, True)
            
            self.btn_exit_yes = Button("YES", SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT//2 + 50, 140, 60, OU_CRIMSON)
            self.btn_exit_no = Button("NO", SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 + 50, 140, 60, GRAY)
            
            self.btn_exit_yes.draw(self.screen, self.font)
            self.btn_exit_no.draw(self.screen, self.font)

    def draw_door_view(self):
        # Full screen background
        bg = pygame.transform.scale(self.door_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(bg, (0, 0))        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0,0))
        # Details
        boss = self.profs[self.selected_door["level"]]
        draw_text(self.screen, f"OFFICE OF {boss.name.upper()}", SCREEN_WIDTH//2, 100, self.title_font, GOLD, center=True)
        draw_text(self.screen, boss.level_name, SCREEN_WIDTH//2, 180, self.font, WHITE, center=True)

        self.btn_confirm = Button("CHALLENGE", SCREEN_WIDTH//2 - 210, SCREEN_HEIGHT - 150, 200, 60, OU_CRIMSON)
        self.btn_back = Button("BACK", SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT - 150, 200, 60, GRAY)
        
        self.btn_confirm.draw(self.screen, self.font)
        self.btn_back.draw(self.screen, self.font)

    def update_hallway(self):
        keys = pygame.key.get_pressed()
        speed = 10
        
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
            self.state = self.next_state
            self.fade_direction = -1

        # finished fading back in
        elif self.fade_alpha <= 0:
            self.fade_alpha = 0
            self.fading = False

        self.fade_surface.set_alpha(self.fade_alpha)
        self.screen.blit(self.fade_surface, (0, 0))


    def draw_menu(self):
        draw_text(self.screen, "Ctrl+Alt+Defeat", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - int(SCREEN_HEIGHT * 0.05), self.title_font, OU_CRIMSON, True)
        self.btn_start = Button("ENTER THE LAB", SCREEN_WIDTH//2 - int(SCREEN_WIDTH * 0.08), SCREEN_HEIGHT//2 + int(SCREEN_HEIGHT * 0.07), int(SCREEN_WIDTH * 0.16), int(SCREEN_HEIGHT * 0.06), OU_CRIMSON)
        self.btn_help = Button("?", int(SCREEN_WIDTH * 0.013), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.08), int(SCREEN_WIDTH * 0.026), int(SCREEN_HEIGHT * 0.05), GRAY)
        self.btn_quit = Button("QUIT", SCREEN_WIDTH - int(SCREEN_WIDTH * 0.08), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.08), int(SCREEN_WIDTH * 0.063), int(SCREEN_HEIGHT * 0.05), GRAY)
        
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
            
            draw_text(self.screen, "SYLLABUS (HOW TO PLAY)", SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + int(SCREEN_HEIGHT * 0.03), self.font, GOLD, True)
            instructions = [
                "1. Pick your Student character.",
                "2. Attack to lower the Professor's HP.",
                "3. Heal when low (but you can't heal at 100%!).",
                "4. When the Prof attacks, answer correctly to DODGE!",
                "5. Defeat all 3 professors to graduate."
            ]
            for i, line in enumerate(instructions):
                draw_text(self.screen, line, SCREEN_WIDTH//5 + int(SCREEN_WIDTH * 0.02), SCREEN_HEIGHT//4 + int(SCREEN_HEIGHT * 0.1) + (i * int(SCREEN_HEIGHT * 0.04)), self.font)
            draw_text(self.screen, "(Click anywhere to close)", SCREEN_WIDTH//2, SCREEN_HEIGHT*0.7, self.font, WHITE, True)

    def draw_character_preview(self, student, rect, facing="right"):
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
        draw_text(self.screen, "CHOOSE YOUR STUDENT", SCREEN_WIDTH//2, int(SCREEN_HEIGHT * 0.06), self.title_font, OU_CREAM, True)
        
        card_w, card_h = int(SCREEN_WIDTH * 0.18), int(SCREEN_HEIGHT * 0.45)
        gap = (SCREEN_WIDTH - (3 * card_w)) // 4
        m_pos = pygame.mouse.get_pos()

        if self.selected_idx is None:
            for i, s in enumerate(self.roster):
                x = gap + i * (card_w + gap)
                y = int(SCREEN_HEIGHT * 0.18)
                rect = pygame.Rect(x, y, card_w, card_h)
                is_hovered = rect.collidepoint(m_pos)
                
                color = GOLD if is_hovered else GRAY
                pygame.draw.rect(self.screen, color, rect, border_radius=15)
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=15)

                preview_rect = pygame.Rect(
                    x + int(card_w * 0.14),
                    y + int(card_h * 0.09),
                    int(card_w * 0.71),
                    int(card_h * 0.54),
                )
                self.draw_character_preview(s, preview_rect)
                draw_text(self.screen, s.name, x + card_w//2, y + int(card_h * 0.68), self.font, WHITE, True)
        else:
            # CENTER AND ENLARGE LOGIC
            s = self.roster[self.selected_idx]
            large_w, large_h = int(SCREEN_WIDTH * 0.23), int(SCREEN_HEIGHT * 0.58)
            x, y = (SCREEN_WIDTH // 2 - large_w // 2), (SCREEN_HEIGHT // 2 - large_h // 2)
            
            # Draw all other cards darkened
            card_w, card_h = int(SCREEN_WIDTH * 0.18), int(SCREEN_HEIGHT * 0.45)
            gap = (SCREEN_WIDTH - (3 * card_w)) // 4
            for i, other in enumerate(self.roster):
                if i == self.selected_idx:
                    continue
                ox = gap + i * (card_w + gap)
                oy = int(SCREEN_HEIGHT * 0.18)
                dark_color = (50, 50, 50)  # darkened gray
                pygame.draw.rect(self.screen, dark_color, (ox, oy, card_w, card_h), border_radius=15)
                pygame.draw.rect(self.screen, WHITE, (ox, oy, card_w, card_h), 2, border_radius=15)

                preview_rect = pygame.Rect(
                    ox + int(card_w * 0.14),
                    oy + int(card_h * 0.09),
                    int(card_w * 0.71),
                    int(card_h * 0.54),
                )
                self.draw_character_preview(other, preview_rect)
                draw_text(self.screen, other.name, ox + card_w//2, oy + int(card_h * 0.68), self.font, WHITE, True)

            # Focused Card
            pygame.draw.rect(self.screen, GOLD, (x, y, large_w, large_h), border_radius=15)
            pygame.draw.rect(self.screen, WHITE, (x, y, large_w, large_h), 4, border_radius=15)

            preview_rect = pygame.Rect(
                x + int(large_w * 0.11),
                y + int(large_h * 0.07),
                int(large_w * 0.78),
                int(large_h * 0.54),
            )
            self.draw_character_preview(s, preview_rect)
            draw_text(self.screen, s.name, x + large_w//2, y + int(large_h * 0.62), self.medium_font, WHITE, True)

            draw_text(self.screen, "SPECIAL ABILITY:", x + int(large_w * 0.09), y + int(large_h * 0.72), self.small_font, GOLD)
            lines = wrap_text(s.ability_desc, self.small_font, int(large_w * 0.82))
            for j, line in enumerate(lines):
                draw_text(self.screen, line, x + int(large_w * 0.09), y + int(large_h * 0.78) + (j * int(SCREEN_HEIGHT * 0.022)), self.small_font, WHITE)

            self.btn_confirm = Button("START SEMESTER", SCREEN_WIDTH//2 - int(SCREEN_WIDTH * 0.08), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.12), int(SCREEN_WIDTH * 0.16), int(SCREEN_HEIGHT * 0.06), OU_CRIMSON)
            self.btn_confirm.draw(self.screen, self.font)

    def show_combat_text(self, text, color=GRAY):
        self.combat_text = text
        self.combat_text_color = color
        self.combat_text_timer = pygame.time.get_ticks() + 2000
        self.combat_text_y_offset = -30


    def draw_battle(self):
        # Floor
        pygame.draw.rect(self.screen, (30, 30, 35), (0, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.3), SCREEN_WIDTH, int(SCREEN_HEIGHT * 0.3)))
        
        self.player.draw(self.screen, int(SCREEN_WIDTH * 0.08), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.55))
        boss_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.65)

        # ----- Boss entrance walking -----
        if self.boss_entering:
            self.boss.set_state(WALK)

            self.boss_x -= self.boss_walk_speed

            if self.boss_x <= self.boss_target_x:
                self.boss_x = self.boss_target_x
                self.boss_entering = False
                self.boss.set_state(IDLE)

        self.boss.draw(self.screen, self.boss_x, boss_y)

        
        # UI Header
        p_hp_ratio = self.player.hp / self.player.max_hp
        b_hp_ratio = self.boss.hp / self.boss.max_hp
        hp_bar_w = int(SCREEN_WIDTH * 0.18)
        hp_bar_h = int(SCREEN_HEIGHT * 0.03)
        pygame.draw.rect(self.screen, OU_CRIMSON, (int(SCREEN_WIDTH * 0.026), int(SCREEN_HEIGHT * 0.05), hp_bar_w, hp_bar_h))
        pygame.draw.rect(self.screen, GREEN, (int(SCREEN_WIDTH * 0.026), int(SCREEN_HEIGHT * 0.05), hp_bar_w * p_hp_ratio, hp_bar_h))
        draw_text(self.screen, f"{self.player.name}: {self.player.hp} HP", int(SCREEN_WIDTH * 0.026), int(SCREEN_HEIGHT * 0.02), self.font)

        boss_bar_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.026) - hp_bar_w
        pygame.draw.rect(self.screen, OU_CRIMSON, (boss_bar_x, int(SCREEN_HEIGHT * 0.05), hp_bar_w, hp_bar_h))
        pygame.draw.rect(self.screen, GREEN, (boss_bar_x, int(SCREEN_HEIGHT * 0.05), hp_bar_w * b_hp_ratio, hp_bar_h))
        boss_hp_text = f"{self.boss.name}: {self.boss.hp} HP"
        boss_hp_surface = self.font.render(boss_hp_text, True, WHITE)
        boss_hp_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.026) - boss_hp_surface.get_width()
        self.screen.blit(boss_hp_surface, (boss_hp_x, int(SCREEN_HEIGHT * 0.02)))

        # Control Box
        ui_rect = pygame.Rect(int(SCREEN_WIDTH * 0.026), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.19), SCREEN_WIDTH - int(SCREEN_WIDTH * 0.052), int(SCREEN_HEIGHT * 0.16))
        pygame.draw.rect(self.screen, BLACK, ui_rect, border_radius=15)
        pygame.draw.rect(self.screen, OU_CRIMSON, ui_rect, 4, border_radius=15)

        # --- Combat Text Animation ---
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
            
            # Render each line
            for i, line in enumerate(lines):
                txt_surface = big_font.render(line, True, self.combat_text_color)
                txt_surface.set_alpha(alpha)
                
                # Position from left side of screen, offset each line
                text_x = int(SCREEN_WIDTH * 0.026)
                text_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.6) + self.combat_text_y_offset + (i * line_height)
                
                self.screen.blit(txt_surface, (text_x, text_y))

     #   if self.player.current_speech and pygame.time.get_ticks() < self.player.speech_timer:
            '''# Note: We pass a negative width to draw_speech_bubble or adjust X 
            # so the bubble tail points to the player.
            # Using your ui.py logic:
            draw_speech_bubble(
                self.screen,
                self.player.current_speech,
                SCREEN_WIDTH - 750,
                SCREEN_HEIGHT - 600,
                self.font,
                type="player"
            )'''

            
        if self.show_question:
            draw_speech_bubble(
                self.screen,
                self.current_q['text'],
                SCREEN_WIDTH - int(SCREEN_WIDTH * 0.23),
                SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.65),
                self.font,
                type="boss"
            )
            self.answer_btns = []
            num_choices = len(self.current_q['choices'])
            btn_width = int(SCREEN_WIDTH * 0.16)
            btn_spacing = int(SCREEN_WIDTH * 0.015)
            total_width = (num_choices * btn_width) + ((num_choices - 1) * btn_spacing)
            start_x = (SCREEN_WIDTH - total_width) // 2

            for i, opt in enumerate(self.current_q['choices']):
                x = start_x + (i * (btn_width + btn_spacing))
                btn = Button(opt, x, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.11), btn_width, int(SCREEN_HEIGHT * 0.12), OU_CRIMSON)
                btn.draw(self.screen, self.font)
                self.answer_btns.append(btn)
        else:
            draw_text(self.screen, self.battle_log, int(SCREEN_WIDTH * 0.042), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.12), self.font)
            btn_width = int(SCREEN_WIDTH * 0.12)
            btn_height = int(SCREEN_HEIGHT * 0.055)
            btn_spacing = int(SCREEN_WIDTH * 0.015)
            self.btn_atk = Button("ATTACK", SCREEN_WIDTH - (2 * btn_width + btn_spacing) - int(SCREEN_WIDTH * 0.035), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.105), btn_width, btn_height, GRAY)
            heal_disabled = (self.player.numHeals <= 0) or (self.player.hp >= self.player.max_hp)
            self.btn_heal = Button("HEAL", SCREEN_WIDTH - btn_width - int(SCREEN_WIDTH * 0.035), SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.105), btn_width, btn_height, GRAY, disabled=heal_disabled)
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
            
            # Stage 3: animations are frozen, fade is happening - do nothing, just keep drawing

    def handle_battle_click(self, mouse_pos):
        if self.boss_entering or self.victory_stage > 0:
            return

        if not self.show_question:
            if self.btn_atk and self.btn_atk.is_clicked(mouse_pos):
                dmg, msg, is_special = self.player.calculate_attack()
                self.show_combat_text(msg, GOLD if is_special else GRAY)

                self.boss.hp -= dmg
                self.player.play_animation("slash", "right", 6)
                self.boss.play_animation("hurt", "up", 3)


                
                self.battle_log = f"You dealt {dmg} damage!"

                #or self.show_combat_text(msg) ## self.battle_log = f"You dealt {dmg} damage!"

                if self.boss.hp <= 0: 
                    self.boss.play_animation("hurt", "up", 5, freeze_last=True)
                    self.player.play_animation("spellcast", "left", 6, freeze_last=True)
                    self.victory_timer = pygame.time.get_ticks()
                    self.victory_stage = 1
                    self.is_player_victory = True
                   # self.boss_entering = True
                   # self.boss_x = SCREEN_WIDTH + 200


                else:
                    # Pull a random question for this boss
                    self.show_question = True
                    self.current_q = self.q_manager.get_random_question(self.boss.bossId)
                    self.sound.play_random_voiceline(self.boss.bossId)  # Play a random voiceline for the boss when they ask a question

            elif self.btn_heal and self.btn_heal.is_clicked(mouse_pos):
                amt, msg, is_special = self.player.get_heal_amount()
                self.show_combat_text(msg, GOLD if is_special else GRAY)

                self.player.hp = min(self.player.max_hp, self.player.hp + amt)
              #  self.player.say(msg) # Player says they healed

                
                self.show_question = True
                self.current_q = self.q_manager.get_random_question(self.boss.bossId)
                self.sound.play_random_voiceline(self.boss.bossId)  # Play a random voiceline for the boss when they ask a question
                
                self.player.numHeals -= 1 # Decrease the number of heals left
                
        else:
            for btn in self.answer_btns:
                if btn.is_clicked(mouse_pos):
                    # Get the correct answer from the JSON
                    correct_index = self.current_q['correct']
                    correct_answer = self.current_q['choices'][correct_index]

                    if btn.text == correct_answer:
                        self.battle_log = "CORRECT! You dodged the grade deduction!"
                    else:
                        if self.player.name == "Cs Get Degrees" and random.random() < 0.25:
                            self.battle_log = "WRONG! But the curve saved you!"
                        else:
                            dmg = self.boss.attack_power
                            self.player.hp -= dmg
                            self.boss.play_animation("spellcast", "down", 7)
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
               


    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK)
            m_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_how_to_play:
                        self.show_how_to_play = False
                    elif self.state == MENU:
                        if self.btn_start and self.btn_start.is_clicked(m_pos): self.state = SELECT
                        if self.btn_help and self.btn_help.is_clicked(m_pos): self.show_how_to_play = True
                        if self.btn_quit and self.btn_quit.is_clicked(m_pos): running = False
                    elif self.state == SELECT:
                        if self.btn_confirm and self.btn_confirm.is_clicked(m_pos):
                            self.player = self.roster[self.selected_idx]
                            self.player.facing = "right"
                            self.player.set_state(IDLE)
                            self.player_world_x = 400 
                            
                            # GO TO HALLWAY
                            self.start_fade(HALLWAY)
                        card_w = int(SCREEN_WIDTH * 0.18)
                        card_h = int(SCREEN_HEIGHT * 0.45)
                        gap = (SCREEN_WIDTH - (3 * card_w)) // 4

                        # If no card selected, normal selection
                        if self.selected_idx is None:
                            for i in range(3):
                                if pygame.Rect(gap + i*(card_w+gap), int(SCREEN_HEIGHT * 0.18), card_w, card_h).collidepoint(m_pos):
                                    self.selected_idx = i

                        else:
                            # If card is selected, click logic
                            large_w, large_h = int(SCREEN_WIDTH * 0.23), int(SCREEN_HEIGHT * 0.58)
                            x, y = (SCREEN_WIDTH // 2 - large_w // 2), (SCREEN_HEIGHT // 2 - large_h // 2)
                            focused_rect = pygame.Rect(x, y, large_w, large_h)
                            '''
                            # Confirm button already handled
                            if self.btn_confirm and self.btn_confirm.is_clicked(m_pos):
                                self.player = self.roster[self.selected_idx]
                                self.boss = self.profs[self.current_level]
                                self.start_fade(BATTLE)
                                self.boss_entering = True
                                self.boss_x = SCREEN_WIDTH + int(SCREEN_WIDTH * 0.1)


                                self.battle_log = f"{self.boss.name} is ready to grade!"
                                intro_file = os.path.join(AUDIO_DIR, f"Prof{self.current_level+1}Intro.wav")
                                self.sound.play_voice(intro_file)
                            
                            # Click outside the focused card cancels selection
                            elif not focused_rect.collidepoint(m_pos):
                                self.selected_idx = None
                            '''
                            if not focused_rect.collidepoint(m_pos) and not self.btn_confirm.is_clicked(m_pos):
                                self.selected_idx = None

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
                                is_near = distance < 100
                                is_unlocked = door["level"] <= self.current_level
                                
                                if door["rect"] and door["rect"].collidepoint(m_pos) and is_unlocked and is_near:
                                    self.selected_door = door
                                    self.state = DOOR_VIEW
                    elif self.state == DOOR_VIEW:
                        if self.btn_confirm.is_clicked(m_pos):
                            self.boss = self.profs[self.selected_door["level"]]
                            self.start_fade(BATTLE)
                            #TODO cant hear sridhar
                            intro_file = f"assets/audio//Prof{self.boss.bossId}Intro.wav"
                            self.sound.play_voice(intro_file)
                            self.player.facing = "right"
                            self.boss.facing = "left"
                            self.boss.hp = self.boss.max_hp
                            self.boss.set_state(IDLE)
                    
                            self.start_fade(BATTLE)
                            self.boss_entering = True
                            self.boss_x = SCREEN_WIDTH + 200
                        elif self.btn_back.is_clicked(m_pos):
                            self.state = HALLWAY
                    elif self.state == BATTLE:
                        self.handle_battle_click(m_pos)
                    elif self.state in [WIN, LOSS]:
                        # Update progress if they won
                        if self.state == WIN and self.current_level < 2:
                            self.current_level += 1
                            self.battle_log = f"Level {self.current_level + 1} Unlocked!"
                        elif self.state == LOSS:
                            self.battle_log = "Try again, student!"

                        # Reset Player stats and animations
                        self.player.hp = self.player.max_hp
                        self.player.override_frames = None
                        self.player.override_index = 0
                        self.player.set_state(IDLE)
                        
                        # Clean up boss/battle variables
                        self.victory_stage = 0
                        self.boss_entering = True
                        self.show_question = False
                        
                        # THE BIG MOVE: Always back to the Hallway
                        self.start_fade(HALLWAY)

            if self.state == MENU: self.draw_menu()
            elif self.state == SELECT: self.draw_character_select()
            elif self.state == HALLWAY: 
                self.update_hallway()
                self.draw_hallway()
            elif self.state == DOOR_VIEW: self.draw_door_view()
            elif self.state == BATTLE: self.draw_battle()
            elif self.state == WIN:
                draw_text(self.screen, self.player.win_msg, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, self.font, GREEN, True)
                draw_text(self.screen, "Click to Continue", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + int(SCREEN_HEIGHT * 0.1), self.small_font, WHITE, True)
            elif self.state == LOSS:
                draw_text(self.screen, self.boss.loss_msg, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, self.font, OU_CRIMSON, True)
                draw_text(self.screen, "Return to Menu", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + int(SCREEN_HEIGHT * 0.1), self.small_font, WHITE, True)
                self.player.hp = self.player.max_hp
                self.boss.hp = self.boss.max_hp

            self.handle_fade()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    Game().run() 