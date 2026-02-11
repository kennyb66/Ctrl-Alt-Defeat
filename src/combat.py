import os
import random
import pygame
from src.constants import GOLD, GRAY, IDLE


class CombatHandler:
    def show_combat_text(self, game, text: str, color=GRAY):
        game.combat_text = text
        game.combat_text_color = color
        game.combat_text_timer = pygame.time.get_ticks() + 2000
        game.combat_text_y_offset = -30

    def handle_battle_click(self, game, mouse_pos):
        if game.boss_entering or game.victory_stage > 0:
            return

        if not game.show_question:
            self._handle_action_click(game, mouse_pos)
        else:
            self._handle_answer_click(game, mouse_pos)

    def _handle_action_click(self, game, mouse_pos):
        if game.btn_atk and game.btn_atk.is_clicked(mouse_pos):
            dmg, msg, is_special = game.player.calculate_attack()

            if is_special:
                game.sound.play_sfx(os.path.join(game.sfx_dir, "critical_hit.wav"), volume=0.1)
            else:
                game.sound.play_sfx(os.path.join(game.sfx_dir, "punch_sound.wav"), volume=0.1)

            self.show_combat_text(game, msg, GOLD if is_special else GRAY)

            game.boss.hp -= dmg
            game.flash_timer = 5
            game.player.play_animation("slash", "right", 6)
            game.boss.play_animation("hurt", "up", 3)
            game.battle_log = f"You dealt {dmg} damage!"

            if game.boss.hp <= 0:
                self._trigger_player_victory(game)
            else:
                self._ask_question(game)

        elif game.btn_heal and game.btn_heal.is_clicked(mouse_pos):
            amt, msg, is_special = game.player.get_heal_amount()
            self.show_combat_text(game, msg, GOLD if is_special else GRAY)
            game.player.hp = min(game.player.max_hp, game.player.hp + amt)
            game.player.numHeals -= 1
            self._ask_question(game)

    def _handle_answer_click(self, game, mouse_pos):
        for btn in game.answer_btns:
            if not btn.is_clicked(mouse_pos):
                continue

            correct_index = game.current_q["correct"]
            correct_answer = game.current_q["choices"][correct_index]

            if btn.text == correct_answer:
                game.battle_log = "CORRECT! You dodged the grade deduction!"
                self.show_combat_text(game, "DODGED!", (0, 255, 255))
                game.sound.play_sfx(os.path.join(game.sfx_dir, "dodge.mp3"), volume=0.1)
            else:
                if game.player.name == "Cs Get Degrees" and random.random() < 0.25:
                    game.battle_log = "WRONG! But the curve saved you!"
                else:
                    dmg = game.boss.attack_power
                    game.player.hp -= dmg
                    game.boss.play_animation("spellcast", "down", 6)
                    game.player.play_animation("hurt", "up", 3)
                    game.battle_log = f"INCORRECT! Lost {dmg} HP!"

            game.show_question = False

            if game.player.hp <= 0:
                self._trigger_boss_victory(game)
            break

    def _ask_question(self, game):
        game.show_question = True
        game.current_q = game.q_manager.get_random_question(game.boss.bossId)
        volume = 0.3 if game.boss.bossId in (2, 3) else 1.0
        game.sound.play_random_voiceline(game.boss.bossId, volume=volume)

    def _trigger_player_victory(self, game):
        game.boss.play_animation("hurt", "up", 5, freeze_last=True)
        game.player.play_animation("spellcast", "right", 6, freeze_last=True)
        game.victory_timer = pygame.time.get_ticks()
        game.victory_stage = 1
        game.is_player_victory = True
        game.sound.clear_music()
        game.sound.play_voice(os.path.join(game.sfx_dir, "win-sound.wav"), volume=0.3)

    def _trigger_boss_victory(self, game):
        game.player.play_animation("hurt", "up", 5, freeze_last=True)
        game.boss.play_animation("spellcast", "left", 6, freeze_last=True)
        game.victory_timer = pygame.time.get_ticks()
        game.victory_stage = 1
        game.is_player_victory = False
        game.sound.clear_music()
        game.sound.play_voice(os.path.join(game.sfx_dir, "lose_sound.wav"), volume=0.2)

    def transition_to_battle(self, game):
        import os
        game.battle_start_time = pygame.time.get_ticks()
        game.boss = game.profs[game.selected_door["level"]]

        intro_file = os.path.join(game.audio_dir, f"Prof{game.boss.bossId}Intro.wav")
        volume = 0.3 if game.boss.bossId in (2, 3) else 1.0
        game.sound.play_voice(intro_file, volume=volume)

        game.player.facing = "right"
        game.boss.facing = "left"
        game.boss.hp = game.boss.max_hp
        game.player.set_state(IDLE)
        game.boss.set_state(IDLE)

        game.boss.override_frames = None
        game.boss.override_index = 0
        game.boss.freeze_last_frame = False

        game.start_fade("BATTLE")
        game.boss_entering = True
        game.boss_x = game.screen.get_width() + 200