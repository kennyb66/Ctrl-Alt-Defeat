import os
import pygame

from src.constants import *
from src.ui import Button
from src.dataGen import QuestionManager
from src.soundGen import SoundManager
from src.asset_loader import AssetLoader
from src.renderer import Renderer
from src.combat import CombatHandler
from src.data_setup import create_roster, create_profs
from src.hallway import HallwayManager

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
SPRITE_DIR = os.path.join(BASE_DIR, "assets", "characters")
SFX_DIR   = os.path.join(BASE_DIR, "assets", "audio", "sfx")
pygame.init()
pygame.mixer.init()

class Game:
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH = self.screen.get_width()
        SCREEN_HEIGHT = self.screen.get_height()

        self.sound = SoundManager()
        self.assets = AssetLoader(self.screen, BASE_DIR)
        self.renderer = Renderer()
        self.combat = CombatHandler()
        self.hallway = HallwayManager()

        self.audio_dir = AUDIO_DIR
        self.sfx_dir = SFX_DIR

        self.state = MENU
        self.last_music_state = None
        self.show_how_to_play = False
        self.selected_idx = None
        self.current_level = 0
        self.show_exit_prompt = False
        self.flash_timer = 0

        self.player = None
        self.boss = None

        self.battle_log = ""
        self.show_question = False
        self.current_q = None
        self.answer_btns = []

        self.combat_text = ""
        self.combat_text_color = GOLD
        self.combat_text_timer = 0
        self.combat_text_y_offset = 0

        self.victory_timer = 0
        self.victory_stage = 0
        self.is_player_victory = True

        self.btn_start = None
        self.btn_help = None
        self.btn_quit = None
        self.btn_confirm = None
        self.btn_back = None
        self.btn_atk = None
        self.btn_heal = None

        self.fading = False
        self.fade_alpha = 0
        self.fade_speed = 12
        self.fade_direction = 1  # 1 = fade to black, -1 = fade from black
        self.next_state = None
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill(BLACK)

        self.floor_h = int(SCREEN_HEIGHT * 0.20)
        self.floor_y = SCREEN_HEIGHT - self.floor_h
        self.door_w = int(SCREEN_WIDTH * 0.15)
        self.door_h = int(SCREEN_HEIGHT * 0.38)
        self.door_y = self.floor_y - self.door_h
        self.door_interact_dist = int(SCREEN_WIDTH * 0.05)

        self.player_world_x = int(SCREEN_WIDTH * 0.2)
        self.player_screen_x = self.player_world_x
        self.hallway_width = SCREEN_WIDTH * 4
        self.camera_x = 0
        self.selected_door = None
        self.doors_previously_near = set()

        door_positions = [0.1, 0.2, 0.3]
        self.door_locations = [
            {"x": int(self.hallway_width * p), "level": i, "rect": None}
            for i, p in enumerate(door_positions)
        ]

        self.boss_entering = False
        self.boss_x = SCREEN_WIDTH + int(SCREEN_WIDTH * 0.1)
        self.boss_target_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.30)
        self.boss_walk_speed = int(SCREEN_WIDTH * 0.003)

        self.roster = create_roster(SPRITE_DIR)
        self.profs = create_profs(SPRITE_DIR)
        self.q_manager = QuestionManager()


    def start_fade(self, next_state: str):
        self.fading = True
        self.fade_direction = 1
        self.fade_alpha = 0
        self.next_state = next_state

    def _handle_fade(self):
        if not self.fading:
            return

        self.fade_alpha += self.fade_speed * self.fade_direction

        if self.fade_alpha >= 255:
            self.fade_alpha = 255
            if self.next_state == MENU:
                self._reset_game()
            self.state = self.next_state
            self.fade_direction = -1
        elif self.fade_alpha <= 0:
            self.fade_alpha = 0
            self.fading = False

        self.fade_surface.set_alpha(self.fade_alpha)
        self.screen.blit(self.fade_surface, (0, 0))

    def _reset_game(self):
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
        self.battle_buttons_locked = False
        self.boss_entering = False
        self.selected_door = None
        self.doors_previously_near = set()

    def _on_menu_click(self, m_pos):
        self._reset_game()
        if self.btn_start and self.btn_start.is_clicked(m_pos):
            self.state = SELECT
        if self.btn_help and self.btn_help.is_clicked(m_pos):
            self.show_how_to_play = True
        if self.btn_quit and self.btn_quit.is_clicked(m_pos):
            return False # signal quit
        return True

    def _on_select_click(self):
        if self.selected_idx is not None:
            self.player = self.roster[self.selected_idx]
            self.start_fade(HALLWAY)

    def _on_hallway_click(self, m_pos):
        if self.show_exit_prompt:
            if self.btn_exit_yes.is_clicked(m_pos):
                self.show_exit_prompt = False
                self.start_fade(MENU)
            elif self.btn_exit_no.is_clicked(m_pos):
                self.show_exit_prompt = False
                self.player_world_x = 150
        else:
            for door in self.door_locations:
                dist = abs(self.player_world_x - door["x"])
                is_near = dist < self.door_interact_dist
                is_unlocked = door["level"] <= self.current_level
                if door["rect"] and door["rect"].collidepoint(m_pos) and is_unlocked and is_near:
                    self.selected_door = door
                    self.state = DOOR_VIEW

    def _on_door_view_click(self, m_pos):
        if self.btn_confirm.is_clicked(m_pos):
            self.combat.transition_to_battle(self)
        elif self.btn_back.is_clicked(m_pos):
            self.state = HALLWAY

    def _on_win_loss_click(self):
        if self.state == WIN:
            if self.current_level >= 2:
                self.start_fade(TOTAL_WIN)
                return
            self.current_level += 1
            self.battle_log = f"Level {self.current_level + 1} Unlocked!"
        else:
            self.battle_log = "Try again, student!"

        self.player.hp = self.player.max_hp
        self.player.override_frames = None
        self.player.override_index = 0
        self.player.set_state(IDLE)
        self.victory_stage = 0
        self.boss_entering = True
        self.show_question = False
        self.start_fade(HALLWAY)

    def _on_total_win_click(self, m_pos):
        if hasattr(self, "btn_exit_win") and self.btn_exit_win.is_clicked(m_pos):
            self._reset_game()
            self.start_fade(MENU)

    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK)
            m_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    #press p to instantly defeat (debug)
                    if event.key == pygame.K_p and self.state == BATTLE:
                        self.boss.hp = 0
                        self.boss.play_animation("hurt", "up", 5, freeze_last=True)
                        self.player.play_animation("spellcast", "right", 6, freeze_last=True)
                        self.victory_timer = pygame.time.get_ticks()
                        self.victory_stage = 1
                        self.is_player_victory = True
                        self.sound.clear_music()
                        self.sound.play_voice(
                            os.path.join(SFX_DIR, "win-sound.wav"), volume=0.3
                        )

                    if event.key == pygame.K_SPACE and self.state == DOOR_VIEW:
                        self.combat.transition_to_battle(self)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_how_to_play:
                        self.show_how_to_play = False
                    elif self.state == MENU:
                        if not self._on_menu_click(m_pos):
                            running = False
                    elif self.state == SELECT:
                        self._on_select_click()
                    elif self.state == HALLWAY:
                        self._on_hallway_click(m_pos)
                    elif self.state == DOOR_VIEW:
                        self._on_door_view_click(m_pos)
                    elif self.state == BATTLE:
                        self.combat.handle_battle_click(self, m_pos)
                    elif self.state in (WIN, LOSS):
                        self._on_win_loss_click()
                    elif self.state == TOTAL_WIN:
                        self._on_total_win_click(m_pos)

            if self.state == MENU:
                self.renderer.draw_menu(self)
            elif self.state == SELECT:
                self.renderer.draw_character_select(self)
            elif self.state == HALLWAY:
                self.hallway.update(self)
                self.renderer.draw_hallway(self)
            elif self.state == DOOR_VIEW:
                self.renderer.draw_door_view(self)
            elif self.state == BATTLE:
                self.renderer.draw_battle(self)
            elif self.state == WIN:
                self.renderer.draw_win(self)
            elif self.state == LOSS:
                self.renderer.draw_loss(self)
                # Reset HP so re-entering the hallway starts fresh
                self.player.hp = self.player.max_hp
                self.boss.hp = self.boss.max_hp
            elif self.state == TOTAL_WIN:
                self.renderer.draw_total_win(self)

            self._handle_fade()

            if self.assets.custom_cursor:
                self.screen.blit(self.assets.custom_cursor, self.assets.custom_cursor.get_rect(topleft=m_pos))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    Game().run()