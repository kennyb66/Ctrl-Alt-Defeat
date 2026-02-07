import pygame
import random
import os
from src.constants import *
from src.entities import Student, Professor
from src.ui import Button, draw_text, draw_speech_bubble, wrap_text
from src.dataGen import load_questions
from src.soundGen import play_audio_clip
from src.soundGen import play_random_voiceline

pygame.init()
pygame.mixer.init()  # This is required to play sounds

class Game:
    def __init__(self):
        pygame.init()
        # macOS specific: center the window
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        
        # Responsive fonts
        self.font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.025))
        self.title_font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.07), bold=True)
        self.small_font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.02))
        
        # Initialize question manager
        from src.dataGen import QuestionManager
        self.q_manager = QuestionManager()
        
        self.state = MENU
        self.show_how_to_play = False
        self.selected_idx = None
        self.current_level = 0
        
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

    def setup_data(self):
        self.roster = [
            Student("Cs Get Degrees", 100, 15, "Hidden Ability: 25% chance to ignore a wrong answer on a dodge.", "C's Get Degrees! You passed!"),
            Student("4.0 Medallion", 100, 20, "Special: 20% Critical Hit chance (The Curve) for 1.5x damage.", "Academic Excellence!"),
            Student("TA God", 100, 18, "Special: Healing restores 50% more HP (Lab Snacks).", "The lab is yours now!")
        ]
        self.profs = [
            Professor("Prof Sridhar", 150, 20, "Logic is not O(1). You fail Data Structures.", "Top Floor Devon", bossId=1),
            Professor("Prof Maiti", 100, 15, "Compiling error... You fail Java 2.", "Library Lawn", bossId=2),
            Professor("Prof Diochnos", 200, 25, "Model Underfitted. You fail ML.", "The Clouds", bossId=3)
        ]


    def load_questions(self):
        self.questions = {}
        all_questions = load_questions()
        for q in all_questions:
            if q["id"] not in self.questions:
                self.questions[q["id"]] = []
            self.questions[q["id"]].append(q)

    def draw_menu(self):
        draw_text(self.screen, "Ctrl+Alt+Defeat", SCREEN_WIDTH//2, SCREEN_HEIGHT//3, self.title_font, OU_CRIMSON, True)
        self.btn_start = Button("ENTER THE LAB", SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2, 300, 60, OU_CRIMSON)
        self.btn_help = Button("?", SCREEN_WIDTH - 80, 30, 50, 50, GRAY)
        self.btn_quit = Button("QUIT", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 80, 120, 50, GRAY)
        
        self.btn_start.draw(self.screen, self.font)
        self.btn_help.draw(self.screen, self.font)
        self.btn_quit.draw(self.screen, self.font)

        if self.show_how_to_play:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            self.screen.blit(overlay, (0,0))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH//4, SCREEN_HEIGHT//4, SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 3)
            draw_text(self.screen, "SYLLABUS (HOW TO PLAY)", SCREEN_WIDTH//2, SCREEN_HEIGHT//4 + 30, self.font, GOLD, True)
            instructions = [
                "1. Pick your Student character.",
                "2. Attack to lower the Professor's HP.",
                "3. Heal when low (but you can't heal at 100%!).",
                "4. When the Prof attacks, answer correctly to DODGE!",
                "5. Defeat all 3 professors to graduate."
            ]
            for i, line in enumerate(instructions):
                draw_text(self.screen, line, SCREEN_WIDTH//4 + 40, SCREEN_HEIGHT//4 + 100 + (i*40), self.font)
            draw_text(self.screen, "(Click anywhere to close)", SCREEN_WIDTH//2, SCREEN_HEIGHT*0.7, self.font, WHITE, True)

    def draw_character_select(self):
        draw_text(self.screen, "CHOOSE YOUR STUDENT", SCREEN_WIDTH//2, 60, self.title_font, OU_CREAM, True)
        
        card_w, card_h = 350, 450
        gap = (SCREEN_WIDTH - (3 * card_w)) // 4
        m_pos = pygame.mouse.get_pos()

        if self.selected_idx is None:
            for i, s in enumerate(self.roster):
                x = gap + i * (card_w + gap)
                y = 180
                rect = pygame.Rect(x, y, card_w, card_h)
                is_hovered = rect.collidepoint(m_pos)
                
                color = GOLD if is_hovered else GRAY
                pygame.draw.rect(self.screen, color, rect, border_radius=15)
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=15)
                
                pygame.draw.rect(self.screen, BLACK, (x+50, y+40, card_w-100, 200), border_radius=10)
                draw_text(self.screen, s.name, x + card_w//2, y + 260, self.font, WHITE, True)
        else:
            # CENTER AND ENLARGE LOGIC
            s = self.roster[self.selected_idx]
            large_w, large_h = 450, 580
            x, y = (SCREEN_WIDTH // 2 - large_w // 2), (SCREEN_HEIGHT // 2 - large_h // 2)
            
            # Focused Card
            pygame.draw.rect(self.screen, GOLD, (x, y, large_w, large_h), border_radius=15)
            pygame.draw.rect(self.screen, WHITE, (x, y, large_w, large_h), 4, border_radius=15)
            
            pygame.draw.rect(self.screen, BLACK, (x+50, y+40, large_w-100, 280), border_radius=10)
            draw_text(self.screen, s.name, x + large_w//2, y + 340, self.title_font, WHITE, True)
            
            draw_text(self.screen, "SPECIAL ABILITY:", x + 40, y + 420, self.font, GOLD)
            lines = wrap_text(s.ability_desc, self.small_font, large_w - 80)
            for j, line in enumerate(lines):
                draw_text(self.screen, line, x + 40, y + 460 + (j*30), self.font, WHITE)

            self.btn_confirm = Button("START SEMESTER", SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 120, 300, 60, OU_CRIMSON)
            self.btn_back = Button("BACK", 50, SCREEN_HEIGHT - 100, 120, 50, GRAY)
            self.btn_confirm.draw(self.screen, self.font)
            self.btn_back.draw(self.screen, self.font)
    def show_combat_text(self, text):
        self.combat_text = text
        self.combat_text_timer = pygame.time.get_ticks() + 1000  # 1 second
        self.combat_text_y_offset = 0

    def draw_battle(self):
        # Floor
        pygame.draw.rect(self.screen, (30, 30, 35), (0, SCREEN_HEIGHT-300, SCREEN_WIDTH, 300))
        
        self.player.draw(self.screen, 250, SCREEN_HEIGHT - 550)
        self.boss.draw(self.screen, SCREEN_WIDTH - 450, SCREEN_HEIGHT - 650)
        
        # UI Header
        p_hp_ratio = self.player.hp / self.player.max_hp
        b_hp_ratio = self.boss.hp / self.boss.max_hp
        pygame.draw.rect(self.screen, OU_CRIMSON, (50, 50, 350, 30))
        pygame.draw.rect(self.screen, GREEN, (50, 50, 350 * p_hp_ratio, 30))
        draw_text(self.screen, f"{self.player.name}: {self.player.hp} HP", 50, 20, self.font)

        pygame.draw.rect(self.screen, OU_CRIMSON, (SCREEN_WIDTH - 400, 50, 350, 30))
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 400, 50, 350 * b_hp_ratio, 30))
        draw_text(self.screen, f"{self.boss.name}: {self.boss.hp} HP", SCREEN_WIDTH - 400, 20, self.font)

        # Control Box
        ui_rect = pygame.Rect(50, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 100, 150)
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
            big_font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.06), bold=True)
            txt_surface = big_font.render(self.combat_text, True, GOLD)
            txt_surface.set_alpha(alpha)

            # position above player
            text_x = 250 + 75 - txt_surface.get_width() // 2
            text_y = SCREEN_HEIGHT - 600 + self.combat_text_y_offset

            self.screen.blit(txt_surface, (text_x, text_y))

        if self.player.current_speech and pygame.time.get_ticks() < self.player.speech_timer:
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
                SCREEN_WIDTH - 450,
                SCREEN_HEIGHT - 650,
                self.font,
                type="boss"
            )
            self.answer_btns = []
            for i, opt in enumerate(self.current_q['choices']):
                btn = Button(opt, SCREEN_WIDTH - 500 + (i*220), SCREEN_HEIGHT - 130, 200, 50, OU_CRIMSON)
                btn.draw(self.screen, self.font)
                self.answer_btns.append(btn)
        else:
            draw_text(self.screen, self.battle_log, 80, SCREEN_HEIGHT - 120, self.font)
            heal_dis = self.player.hp >= self.player.max_hp
            self.btn_atk = Button("ATTACK", SCREEN_WIDTH - 480, SCREEN_HEIGHT - 130, 180, 50, GRAY)
            self.btn_heal = Button("HEAL", SCREEN_WIDTH - 280, SCREEN_HEIGHT - 130, 180, 50, GRAY, disabled=heal_dis)
            self.btn_atk.draw(self.screen, self.font)
            self.btn_heal.draw(self.screen, self.font)

    def handle_battle_click(self, mouse_pos):
        if not self.show_question:
            if self.btn_atk and self.btn_atk.is_clicked(mouse_pos):
                dmg, msg = self.player.calculate_attack()
                self.boss.hp -= dmg

                self.show_combat_text(msg)
                self.battle_log = f"You dealt {dmg} damage!"

                #or self.show_combat_text(msg) ## self.battle_log = f"You dealt {dmg} damage!"

                
                if self.boss.hp <= 0: self.state = WIN
                else:
                    # Pull a random question for this boss
                    self.show_question = True
                    self.current_q = self.q_manager.get_random_question(self.boss.bossId)
                    play_random_voiceline(self.boss.bossId)  # Play a random voiceline for the boss when they ask a question

            elif self.btn_heal and self.btn_heal.is_clicked(mouse_pos):
                amt, msg = self.player.get_heal_amount()
                self.player.hp = min(self.player.max_hp, self.player.hp + amt)
              #  self.player.say(msg) # Player says they healed
                self.show_combat_text(msg)

                
                self.show_question = True
                self.current_q = self.q_manager.get_random_question(self.boss.bossId)
                play_random_voiceline(self.boss.bossId)  # Play a random voiceline for the boss when they ask a question
                
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
                            self.battle_log = f"INCORRECT! Lost {dmg} HP!"

                    # Done showing the question
                    self.show_question = False

                    # Check if the player lost all HP
                    if self.player.hp <= 0:
                        self.state = LOSS



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
                        card_w = 350
                        gap = (SCREEN_WIDTH - (3 * card_w)) // 4
                        for i in range(3):
                            if pygame.Rect(gap + i*(card_w+gap), 200, card_w, 450).collidepoint(m_pos):
                                self.selected_idx = i
                        if self.selected_idx is not None and self.btn_confirm and self.btn_confirm.is_clicked(m_pos):
                            self.player = self.roster[self.selected_idx]
                            self.boss = self.profs[self.current_level]
                            self.state = BATTLE
                            self.battle_log = f"{self.boss.name} is ready to grade."
                            intro_file = f"assets/audio//Prof{self.boss.bossId}Intro.wav"
                            play_audio_clip(intro_file)

                    elif self.state == BATTLE:
                        self.handle_battle_click(m_pos)
                    elif self.state in [WIN, LOSS]:
                        if self.state == WIN and self.current_level < 2:
                            self.current_level += 1
                            self.player.hp = self.player.max_hp
                            self.boss = self.profs[self.current_level]
                            self.state = BATTLE
                            self.battle_log = f"Onto Level {self.current_level+1}!"
                        else: running = False

            if self.state == MENU: self.draw_menu()
            elif self.state == SELECT: self.draw_character_select()
            elif self.state == BATTLE: self.draw_battle()
            elif self.state == WIN:
                draw_text(self.screen, self.player.win_msg, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, self.font, GREEN, True)
                draw_text(self.screen, "Click to Continue", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100, self.small_font, WHITE, True)
            elif self.state == LOSS:
                draw_text(self.screen, self.boss.loss_msg, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, self.font, OU_CRIMSON, True)
                draw_text(self.screen, "Click to Exit", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100, self.small_font, WHITE, True)

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    Game().run()