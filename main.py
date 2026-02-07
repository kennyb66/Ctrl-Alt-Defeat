import pygame
import random
import os
from src.constants import *
from src.entities import Student, Professor
from src.ui import Button, draw_text, draw_speech_bubble, wrap_text

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

    def setup_data(self):
        self.roster = [
            Student("Cs Get Degrees", 100, 15, "Hidden Ability: 25% chance to ignore a wrong answer on a dodge.", "C's Get Degrees! You passed!"),
            Student("4.0 Medallion", 100, 20, "Special: 20% Critical Hit chance (The Curve) for 1.5x damage.", "Academic Excellence!"),
            Student("TA God", 100, 18, "Special: Healing restores 50% more HP (Lab Snacks).", "The lab is yours now!")
        ]
        self.profs = [
            Professor("Prof Maiti", 100, 15, "Compiling error... You fail Java 2.", "Library Lawn"),
            Professor("Prof Sridhar", 150, 20, "Logic is not O(1). You fail Data Structures.", "Top Floor Devon"),
            Professor("Prof Diochnos", 200, 25, "Model Underfitted. You fail ML.", "The Clouds")
        ]

    def load_questions(self):
        self.questions = {
            "Prof Maiti": [
                {"q": "Is 'String' a primitive type in Java?", "a": "No", "options": ["Yes", "No"]},
                {"q": "Which keyword is used for inheritance in Java?", "a": "extends", "options": ["implements", "extends"]}
            ],
            "Prof Sridhar": [
                {"q": "Worst case time complexity for searching a BST?", "a": "O(n)", "options": ["O(log n)", "O(n)"]},
                {"q": "Does a Stack use FIFO or LIFO?", "a": "LIFO", "options": ["FIFO", "LIFO"]}
            ],
            "Prof Diochnos": [
                {"q": "Does a high learning rate cause overshoot?", "a": "Yes", "options": ["Yes", "No"]},
                {"q": "Is K-Means supervised or unsupervised?", "a": "Unsupervised", "options": ["Supervised", "Unsupervised"]}
            ]
        }

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
        draw_text(self.screen, "SELECT YOUR STUDENT", SCREEN_WIDTH//2, 80, self.title_font, OU_CREAM, True)
        
        card_w, card_h = 350, 450
        gap = (SCREEN_WIDTH - (3 * card_w)) // 4
        
        for i, s in enumerate(self.roster):
            x = gap + i * (card_w + gap)
            y = 200
            rect = pygame.Rect(x, y, card_w, card_h)
            
            is_hovered = rect.collidepoint(pygame.mouse.get_pos())
            color = GOLD if (self.selected_idx == i or is_hovered) else GRAY
            
            pygame.draw.rect(self.screen, color, rect, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, rect, 4 if self.selected_idx == i else 2, border_radius=15)
            
            # Character Portrait Placeholder
            pygame.draw.rect(self.screen, BLACK, (x+50, y+40, card_w-100, 200), border_radius=10)
            draw_text(self.screen, s.name, x + card_w//2, y + 260, self.font, WHITE, True)
            
            if self.selected_idx == i:
                draw_text(self.screen, "SPECIAL ABILITY:", x + 20, y + 310, self.font, GOLD)
                lines = wrap_text(s.ability_desc, self.small_font, card_w - 40)
                for j, line in enumerate(lines):
                    draw_text(self.screen, line, x + 20, y + 340 + (j*25), self.small_font, WHITE)

        if self.selected_idx is not None:
            self.btn_confirm = Button("CONFIRM ENROLLMENT", SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 120, 400, 60, OU_CRIMSON)
            self.btn_confirm.draw(self.screen, self.font)

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

        if self.show_question:
            draw_speech_bubble(self.screen, self.current_q['q'], SCREEN_WIDTH - 450, SCREEN_HEIGHT - 600, self.font)
            self.answer_btns = []
            for i, opt in enumerate(self.current_q['options']):
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
                self.battle_log = f"{msg} Dealt {dmg} damage!"
                if self.boss.hp <= 0: self.state = WIN
                else:
                    self.show_question = True
                    self.current_q = random.choice(self.questions[self.boss.name])
            elif self.btn_heal and self.btn_heal.is_clicked(mouse_pos):
                amt = self.player.get_heal_amount()
                self.player.hp = min(self.player.max_hp, self.player.hp + amt)
                self.battle_log = f"Office Hours! Restored {amt} HP."
                self.show_question = True
                self.current_q = random.choice(self.questions[self.boss.name])
        else:
            for btn in self.answer_btns:
                if btn.is_clicked(mouse_pos):
                    # handle_dodge logic integrated
                    if btn.text == self.current_q['a']:
                        self.battle_log = "CORRECT! You dodged the grade deduction!"
                    else:
                        if self.player.name == "Cs Get Degrees" and random.random() < 0.25:
                            self.battle_log = "WRONG! But the curve saved you!"
                        else:
                            dmg = self.boss.attack_power
                            self.player.hp -= dmg
                            self.battle_log = f"INCORRECT! Lost {dmg} HP!"
                    self.show_question = False
                    if self.player.hp <= 0: self.state = LOSS

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