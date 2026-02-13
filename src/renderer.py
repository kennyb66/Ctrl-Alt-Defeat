import math
import random
import pygame
from src.constants import *
from src.ui import Button, draw_text, draw_speech_bubble, wrap_text

class Renderer: #DRAW FCTS
    def draw_transparent_rect(self, surface: pygame.Surface, color, rect: pygame.Rect, alpha: int):
        s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        r, g, b = color
        s.fill((r, g, b, alpha))
        surface.blit(s, (rect.x, rect.y))

    def draw_character_preview(self, game, student, rect: pygame.Rect, facing: str = "front"):
        frame = None
        if hasattr(student, "all_frames"):
            frames = student.all_frames.get(facing, {}).get(IDLE, [])
            if frames:
                frame = frames[0]

        if not frame:
            pygame.draw.rect(game.screen, BLACK, rect, border_radius=10)
            return

        padding = int(min(rect.w, rect.h) * 0.08)
        max_w = rect.w - padding * 2
        max_h = rect.h - padding * 2
        if max_w <= 0 or max_h <= 0:
            return

        fw, fh = frame.get_size()
        scale = min(max_w / fw, max_h / fh)
        tw = max(1, int(fw * scale))
        th = max(1, int(fh * scale))
        sprite = pygame.transform.smoothscale(frame, (tw, th))
        game.screen.blit(sprite, (rect.x + (rect.w - tw) // 2, rect.y + (rect.h - th) // 2))

    def draw_character_with_shadow(self, game, character, x: int, y: int):
        shadow_offset = 5

        if character.override_frames:
            if character.override_index >= len(character.override_frames):
                character.override_index = len(character.override_frames) - 1
            frame = character.override_frames[character.override_index]
        else:
            cur = character.all_frames[character.facing]
            frames = cur.get(character.state, cur[IDLE])
            if not frames or character.current_frame >= len(frames):
                character.current_frame = 0
                if not frames:
                    frames = cur[IDLE]
            if len(frames) == 0:
                return
            frame = frames[character.current_frame]

        shadow = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))
        shadow_color = (0, 0, 0, 150)
        for dx, dy in [(-shadow_offset, 0), (shadow_offset, 0),
                       (0, -shadow_offset), (0, shadow_offset),
                       (-shadow_offset, -shadow_offset), (shadow_offset, shadow_offset),
                       (-shadow_offset, shadow_offset), (shadow_offset, -shadow_offset)]:
            shadow.blit(frame, (0, 0))
            shadow.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)
            game.screen.blit(shadow, (x + dx, y + dy))
        game.screen.blit(frame, (x, y))

    def draw_menu(self, game):
        import os
        from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        assets = game.assets
        screen = game.screen
        font = assets.fonts["normal"]

        screen.blit(assets.background_assets["title"], (0, 0))

        if game.last_music_state != MENU:
            game.sound.clear_music()
            intro_file = os.path.join(game.sfx_dir, "title_screen.wav")
            game.sound.play_music(intro_file)
            game.last_music_state = MENU

        side_margin = 0.025 * SCREEN_WIDTH
        help_w = 0.026 * SCREEN_WIDTH
        quit_w = 0.063 * SCREEN_WIDTH
        help_x = side_margin
        quit_x = SCREEN_WIDTH - side_margin - quit_w

        game.btn_help = Button(
            "?",
            int(help_x),
            SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.08),
            int(SCREEN_HEIGHT * 0.05),
            int(SCREEN_HEIGHT * 0.05),
            OU_CREAM,
        )

        current_ticks = pygame.time.get_ticks()
        wiggle_x = 0
        if (current_ticks % 2500) < 500:
            wiggle_x = math.sin(current_ticks * 0.05) * 6

        btn_w = int(SCREEN_WIDTH * 0.16)
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2 + int(wiggle_x)
        game.btn_start = Button(
            "BEGIN SEMESTER",
            btn_x,
            SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.07),
            btn_w,
            int(SCREEN_HEIGHT * 0.06),
            OU_CREAM,
        )

        game.btn_quit = Button(
            "QUIT",
            int(quit_x),
            SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.08),
            int(quit_w),
            int(SCREEN_HEIGHT * 0.05),
            OU_CREAM,
        )

        game.btn_start.draw(screen, font)
        game.btn_help.draw(screen, font)
        game.btn_quit.draw(screen, font)

        if game.show_how_to_play:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))

            scroll_x = SCREEN_WIDTH // 2 - assets.scroll_bg.get_width() // 2
            scroll_y = SCREEN_HEIGHT // 4
            screen.blit(assets.scroll_bg, (scroll_x, scroll_y))

            draw_text(
                screen,
                "SYLLABUS (HOW TO PLAY)",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 4 + int(SCREEN_HEIGHT * 0.13),
                font, BLACK, True,
            )
            instructions = [
                "1. Pick your Student character.",
                "2. Attack to lower the Professor's HP.",
                "3. Heal when low (but you can't heal at 100%!).",
                "4. When the Prof attacks, answer correctly to DODGE!",
                "5. Defeat all 3 professors to graduate.",
                "6. Walk left of the main hall to exit the game.",
            ]
            for i, line in enumerate(instructions):
                draw_text(
                    screen, line,
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 4 + int(SCREEN_HEIGHT * 0.2) + (i * int(SCREEN_HEIGHT * 0.04)),
                    font, BLACK, True,
                )
            draw_text(screen, "(Click anywhere to close)", SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.7, font, BLACK, True)

    def draw_character_select(self, game):
        assets = game.assets
        screen = game.screen
        font = assets.fonts["normal"]
        medium_font = assets.fonts["medium"]
        small_font = assets.fonts["small"]
        title_font = assets.fonts["title"]

        screen.blit(assets.background_assets["class"], (0, 0))

        if game.last_music_state != SELECT:
            game.last_music_state = SELECT

        title = "CHOOSE YOUR STUDENT"
        tx = SCREEN_WIDTH // 2
        ty = int(SCREEN_HEIGHT * 0.2)
        card_w, card_h = int(SCREEN_WIDTH * 0.18), int(SCREEN_HEIGHT * 0.45)
        total_cards_width = 3 * card_w
        gap = int((SCREEN_WIDTH - total_cards_width) / 4)
        m_pos = pygame.mouse.get_pos()

        for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
            draw_text(screen, title, tx + ox, ty + oy, title_font, BLACK, True)
        draw_text(screen, title, tx, ty, title_font, OU_CREAM, True)

        hover_idx = None
        for i in range(len(game.roster)):
            x = gap + i * (card_w + gap)
            y = int(SCREEN_HEIGHT * 0.35)
            rect = pygame.Rect(x, y, card_w, card_h)
            if rect.collidepoint(m_pos):
                hover_idx = i
                break

        game.selected_idx = hover_idx

        if game.selected_idx is None:
            for i, s in enumerate(game.roster):
                x = gap + i * (card_w + gap)
                y = int(SCREEN_HEIGHT * 0.35)
                rect = pygame.Rect(x, y, card_w, card_h)
                self.draw_transparent_rect(screen, GRAY, rect, 180)
                pygame.draw.rect(screen, WHITE, rect, 2, border_radius=15)
                preview_rect = pygame.Rect(
                    x + int(card_w * 0.14),
                    y + int(card_h * 0.09),
                    int(card_w * 0.71),
                    int(card_h * 0.54),
                )
                self.draw_character_preview(game, s, preview_rect)
                draw_text(screen, s.name, x + card_w // 2, y + int(card_h * 0.68), font, WHITE, True)
        else:
            s_focused = game.roster[game.selected_idx]
            large_w, large_h = int(SCREEN_WIDTH * 0.23), int(SCREEN_HEIGHT * 0.58)

            for i, other in enumerate(game.roster):
                x = gap + i * (card_w + gap)
                y = int(SCREEN_HEIGHT * 0.35)
                rect = pygame.Rect(x, y, card_w, card_h)

                if i == game.selected_idx:
                    fx = x - (large_w - card_w) // 2
                    fy = y - (large_h - card_h) // 2
                    f_rect = pygame.Rect(fx, fy, large_w, large_h)
                    pygame.draw.rect(screen, GOLD, f_rect, border_radius=15)
                    pygame.draw.rect(screen, WHITE, f_rect, 4, border_radius=15)

                    p_rect = pygame.Rect(
                        fx + int(large_w * 0.11),
                        fy + int(large_h * 0.07),
                        int(large_w * 0.78),
                        int(large_h * 0.54),
                    )
                    if hasattr(s_focused, "hover_sprite") and s_focused.hover_sprite:
                        img = s_focused.hover_sprite
                        scale = min(p_rect.w / img.get_width(), p_rect.h / img.get_height())
                        scaled = pygame.transform.smoothscale(
                            img, (int(img.get_width() * scale), int(img.get_height() * scale))
                        )
                        screen.blit(
                            scaled,
                            (p_rect.centerx - scaled.get_width() // 2,
                             p_rect.centery - scaled.get_height() // 2),
                        )
                    else:
                        self.draw_character_preview(game, s_focused, p_rect)

                    draw_text(screen, s_focused.name, fx + large_w // 2, fy + int(large_h * 0.62), medium_font, BLACK, True)
                    small_font.set_bold(True)
                    draw_text(screen, "SPECIAL ABILITY:", fx + large_w // 2, fy + int(large_h * 0.70), small_font, GOLD, True)
                    lines = wrap_text(s_focused.ability_desc, small_font, int(large_w * 0.82))
                    for j, line in enumerate(lines):
                        draw_text(screen, line, fx + large_w // 2, fy + int(large_h * 0.75) + (j * 20), small_font, BLACK, True)
                    small_font.set_bold(False)
                else:
                    self.draw_transparent_rect(screen, GRAY, rect, 180)
                    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=15)
                    p_rect = pygame.Rect(
                        x + int(card_w * 0.14),
                        y + int(card_h * 0.09),
                        int(card_w * 0.71),
                        int(card_h * 0.54),
                    )
                    self.draw_character_preview(game, other, p_rect)
                    draw_text(screen, other.name, x + card_w // 2, y + int(card_h * 0.68), font, WHITE, True)

    def draw_hallway(self, game):
        assets = game.assets
        screen = game.screen
        font = assets.fonts["normal"]
        title_font = assets.fonts["title"]

        start_screen_x = -game.camera_x
        if start_screen_x < SCREEN_WIDTH:
            screen.blit(assets.hallway_start, (start_screen_x, 0))

        if game.camera_x < assets.mid_point:
            current_x = assets.mid_point - game.camera_x
        else:
            offset = (game.camera_x - assets.mid_point) % assets.loop_w
            current_x = -offset

        while current_x < SCREEN_WIDTH:
            screen.blit(assets.hallway_loop, (current_x, 0))
            current_x += assets.loop_w

        doors_currently_near = set()
        import os

        for i, door in enumerate(game.door_locations):
            screen_x = door["x"] - game.camera_x
            if -200 < screen_x < SCREEN_WIDTH:
                distance = abs(game.player_world_x - door["x"])
                is_near = distance < int(SCREEN_WIDTH * 0.05)
                is_unlocked = i <= game.current_level

                if is_near and is_unlocked:
                    doors_currently_near.add(i)

                if is_near and is_unlocked and i not in game.doors_previously_near:
                    door_sound = os.path.join(game.sfx_dir, "dragon-studio-opening-door-sfx-454240.mp3")
                    game.sound.play_sfx(door_sound, volume=0.5)

                if is_near and is_unlocked:
                    img_to_use = assets.door_upclose_img
                else:
                    img_to_use = assets.door_img

                if is_near:
                    display_img = pygame.transform.scale(img_to_use, (game.door_w, game.door_h))
                else:
                    display_img = img_to_use

                if i > game.current_level:
                    display_img = display_img.copy()
                    display_img.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_MULT)

                door_y = game.door_y
                screen.blit(display_img, (screen_x, door_y))
                door["rect"] = pygame.Rect(screen_x, door_y, game.door_w, game.door_h)

        game.doors_previously_near = doors_currently_near

        player_draw_x = game.player_screen_x - int(SCREEN_WIDTH * 0.04)
        player_draw_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.50)
        game.player.update_animation()
        self.draw_character_with_shadow(game, game.player, player_draw_x, player_draw_y)

        if game.show_exit_prompt:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            draw_text(screen, "Return to Menu?", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70, title_font, WHITE, True)

            btn_w = int(SCREEN_WIDTH * 0.07)
            btn_h = int(SCREEN_HEIGHT * 0.07)
            gap = int(SCREEN_WIDTH * 0.02)
            total_w = btn_w * 2 + gap
            start_x = SCREEN_WIDTH // 2 - total_w // 2
            btn_y = SCREEN_HEIGHT // 2 + int(SCREEN_HEIGHT * 0.05)

            game.btn_exit_yes = Button("YES", start_x, btn_y, btn_w, btn_h, OU_CREAM)
            game.btn_exit_no = Button("NO", start_x + btn_w + gap, btn_y, btn_w, btn_h, OU_CREAM)
            game.btn_exit_yes.draw(screen, font)
            game.btn_exit_no.draw(screen, font)

    def draw_door_view(self, game):
        assets = game.assets
        screen = game.screen
        font = assets.fonts["normal"]
        title_font = assets.fonts["title"]

        screen.blit(assets.door_nametage_img, (0, 0))

        boss = game.profs[game.selected_door["level"]]
        lines = f"OFFICE OF\n{boss.name.upper()}".split("\n")
        current_y = int(SCREEN_HEIGHT * 0.35)
        for line in lines:
            draw_text(screen, line, SCREEN_WIDTH // 2, current_y, title_font, BLACK, True)
            current_y += title_font.get_linesize()
        draw_text(screen, boss.level_name, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.53, font, BLACK, center=True)

        current_ticks = pygame.time.get_ticks()
        wiggle_x = math.sin(current_ticks * 0.05) * 6 if (current_ticks % 2500) < 500 else 0

        btn_w = int(SCREEN_WIDTH * 0.13)
        btn_h = int(SCREEN_HEIGHT * 0.08)
        gap = int(SCREEN_WIDTH * 0.01)
        total_w = btn_w * 2 + gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        
        confirm_x = start_x + int(wiggle_x)
        game.btn_confirm = Button("CHALLENGE", confirm_x, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.16), btn_w, btn_h, OU_CREAM)
        game.btn_back = Button("BACK", start_x + btn_w + gap, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.16), btn_w, btn_h, OU_CREAM)
        game.btn_confirm.draw(screen, font)
        game.btn_back.draw(screen, font)

    def draw_battle(self, game):
        import os
        assets = game.assets
        screen = game.screen
        font = assets.fonts["normal"]

        boss_music_id = game.boss.bossId
        if getattr(game, "current_boss_music_id", None) != boss_music_id:
            game.sound.clear_music()
            game.sound.play_music(os.path.join(game.sfx_dir, f"Boss{boss_music_id}_music.wav"), volume=0.1)
            game.current_boss_music_id = boss_music_id

        bg_index = game.boss.bossId - 1
        if 0 <= bg_index < len(assets.battle_backgrounds):
            screen.blit(assets.battle_backgrounds[bg_index], (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))

        floor_height = int(SCREEN_HEIGHT * 0.3)
        floor_y = SCREEN_HEIGHT - floor_height

        box_w, box_h = int(SCREEN_WIDTH * 0.225), int(SCREEN_HEIGHT * 0.09)
        padding = 15
        is_low_health = game.player and game.player.hp <= (game.player.max_hp * 0.3)

        for i, x_pos in enumerate([padding, SCREEN_WIDTH - box_w - padding]):
            bg_color = (0, 0, 0, 160)
            draw_x, draw_y = x_pos, padding
            if is_low_health and i == 0:
                bg_color = (200, 0, 0, 180)
                draw_x += random.randint(-5, 5)
                draw_y += random.randint(-5, 5)
            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(box_surf, bg_color, (0, 0, box_w, box_h), border_radius=12)
            screen.blit(box_surf, (draw_x, draw_y))

        floor_tex = assets.floor_textures.get(game.boss.bossId)
        if floor_tex:
            try:
                scaled_floor = pygame.transform.scale(floor_tex, (SCREEN_WIDTH, floor_height))
                screen.blit(scaled_floor, (0, floor_y + SCREEN_HEIGHT * 0.03))
            except Exception:
                pass

        player_x = int(SCREEN_WIDTH * 0.08)
        player_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.55)
        game.player.update_animation()
        self.draw_character_with_shadow(game, game.player, player_x, player_y)

        boss_y = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.63)
        if game.boss_entering:
            game.boss.set_state(WALK)
            game.boss_x -= game.boss_walk_speed
            if game.boss_x <= game.boss_target_x:
                game.boss_x = game.boss_target_x
                game.boss_entering = False
                game.boss.set_state(IDLE)
        game.boss.update_animation()
        self.draw_character_with_shadow(game, game.boss, game.boss_x, boss_y)

        hp_bar_w = int(SCREEN_WIDTH * 0.18)
        hp_bar_h = int(SCREEN_HEIGHT * 0.03)
        hp_y = int(SCREEN_HEIGHT * 0.05)
        text_y = int(SCREEN_HEIGHT * 0.02)
        ui_margin = int(SCREEN_WIDTH * 0.026)

        p_hp_ratio = game.player.hp / game.player.max_hp
        b_hp_ratio = game.boss.hp / game.boss.max_hp
        player_hp_display = max(0, game.player.hp)
        boss_hp_display = max(0, game.boss.hp)

        pygame.draw.rect(screen, OU_CRIMSON, (ui_margin, hp_y, hp_bar_w, hp_bar_h))
        pygame.draw.rect(screen, GREEN, (ui_margin, hp_y, int(hp_bar_w * p_hp_ratio), hp_bar_h))
        draw_text(screen, f"{game.player.name}: {player_hp_display} HP", ui_margin, text_y, font)

        boss_bar_x = SCREEN_WIDTH - ui_margin - hp_bar_w
        pygame.draw.rect(screen, OU_CRIMSON, (boss_bar_x, hp_y, hp_bar_w, hp_bar_h))
        pygame.draw.rect(screen, GREEN, (boss_bar_x, hp_y, int(hp_bar_w * b_hp_ratio), hp_bar_h))
        boss_text_surf = font.render(f"{game.boss.name}: {boss_hp_display} HP", True, WHITE)
        screen.blit(boss_text_surf, (SCREEN_WIDTH - ui_margin - boss_text_surf.get_width(), text_y))

        btn_width = int(SCREEN_WIDTH * 0.16)
        btn_height = int(SCREEN_HEIGHT * 0.055)
        btn_spacing = int(SCREEN_WIDTH * 0.015)
        btn_margin = int(SCREEN_WIDTH * 0.05)

        ui_rect = pygame.Rect(
            ui_margin,
            SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.18),
            SCREEN_WIDTH - ui_margin * 2,
            int(SCREEN_HEIGHT * 0.15),
        )
        if assets.notebook_paper_img:
            bg_rect = ui_rect.inflate(0, 10)
            bg_img = pygame.transform.smoothscale(assets.notebook_paper_img, (bg_rect.w, bg_rect.h))
            paper_surface = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
            paper_surface.blit(bg_img, (0, 0))
            mask_surface = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), mask_surface.get_rect(), border_radius=15)
            paper_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(paper_surface, (bg_rect.x, bg_rect.y))
        else:
            pygame.draw.rect(screen, BLACK, ui_rect.inflate(0, 10), border_radius=15)
        pygame.draw.rect(screen, OU_CRIMSON, ui_rect, 4, border_radius=15)

        if game.combat_text and pygame.time.get_ticks() < game.combat_text_timer:
            game.combat_text_y_offset -= 0.5
            time_left = game.combat_text_timer - pygame.time.get_ticks()
            alpha = max(0, min(255, int(255 * (time_left / 1000))))
            big_font = pygame.font.SysFont("Courier", int(SCREEN_HEIGHT * 0.05), bold=True)
            lines = game.combat_text.split("\n")
            line_height = big_font.get_height()
            for i, line in enumerate(lines):
                tx = ui_margin + int(SCREEN_WIDTH * 0.075)
                ty = SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.6) + game.combat_text_y_offset + (i * line_height)
                for dx, dy in [(-2, -2), (0, -2), (2, -2),
                               (-2, 0), (2, 0),
                               (-2, 2), (0, 2), (2, 2)]:
                    outline = big_font.render(line, True, BLACK)
                    outline.set_alpha(alpha)
                    screen.blit(outline, (tx + dx, ty + dy))
                txt = big_font.render(line, True, game.combat_text_color)
                txt.set_alpha(alpha)
                screen.blit(txt, (tx, ty))

        if game.show_question:
            draw_speech_bubble(
                screen,
                game.current_q["text"],
                SCREEN_WIDTH - int(SCREEN_WIDTH * 0.23),
                SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.60),
                font,
                type="boss",
            )
            game.answer_btns = []
            num_choices = len(game.current_q["choices"])
            total_width = (num_choices * btn_width) + ((num_choices - 1) * btn_spacing)
            start_x = (SCREEN_WIDTH - total_width) / 2
            for i, opt in enumerate(game.current_q["choices"]):
                x = start_x + (i * (btn_width + btn_spacing))
                btn = Button(
                    opt,
                    int(x),
                    SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.11),
                    btn_width,
                    int(SCREEN_HEIGHT * 0.12),
                    (212, 175, 55, 120),
                    (212, 175, 55),
                )
                btn.draw(screen, font)
                game.answer_btns.append(btn)
        else:
            text_margin = int(SCREEN_WIDTH * 0.07)
            battle_font = assets.fonts["medium"]
            draw_text(screen, game.battle_log, text_margin, SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.12), battle_font, BLACK)

            current_time = pygame.time.get_ticks()
            heal_disabled = (game.player.numHeals <= 0) or (game.player.hp >= game.player.max_hp)
            is_locked = (current_time - getattr(game, "battle_start_time", 0)) < 4500
            atk_color = (128, 128, 128) if is_locked else GOLD

            game.btn_atk = Button(
                "ATTACK",
                SCREEN_WIDTH - btn_margin - 2 * btn_width - btn_spacing,
                SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.105),
                btn_width, btn_height,
                (255, 0, 0), atk_color,
                disabled=is_locked,
            )
            game.btn_heal = Button(
                "HEAL",
                SCREEN_WIDTH - btn_margin - btn_width,
                SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.105),
                btn_width, btn_height,
                GREEN,
                disabled=heal_disabled,
            )
            game.btn_atk.draw(screen, font)
            game.btn_heal.draw(screen, font)

        if game.victory_stage > 0:
            elapsed = pygame.time.get_ticks() - game.victory_timer
            if game.victory_stage == 1 and elapsed > 2000:
                game.victory_stage = 2
                game.victory_timer = pygame.time.get_ticks()
            elif game.victory_stage == 2 and elapsed > 100:
                game.victory_stage = 3
                if game.is_player_victory:
                    game.start_fade(WIN)
                    game.boss_entering = True
                    game.boss_x = SCREEN_WIDTH + 200
                else:
                    game.start_fade(LOSS)

        if game.flash_timer > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill(WHITE)
            flash_surf.set_alpha(100)
            screen.blit(flash_surf, (0, 0))
            game.flash_timer -= 1

    def draw_win(self, game):
        win_bg = "title"
        if game.player:
            name_map = {
                "4.0 Medallion": "win_kris",
                "Cs Get Degrees": "win_shri",
                "TA God": "win_ken",
            }
            win_bg = name_map.get(game.player.name, "title")

        game.screen.blit(game.assets.background_assets[win_bg], (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        game.screen.blit(overlay, (0, 0))

    def draw_loss(self, game):
        boss_bg_map = {1: "lost_sridhar", 2: "lost_dioch", 3: "lost_maiti"}
        bg_key = boss_bg_map.get(game.boss.bossId, "lost_sridhar")
        game.screen.blit(game.assets.background_assets[bg_key], (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        game.screen.blit(overlay, (0, 0))

        draw_text(
            game.screen, game.boss.loss_msg,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.9,
            game.assets.fonts["normal"], OU_CRIMSON, True,
        )

    def draw_total_win(self, game):
        screen = game.screen
        font = game.assets.fonts["normal"]
        medium_font = game.assets.fonts["medium"]

        screen.blit(game.assets.background_assets["end"], (0, 0))

        header_w, header_h = int(SCREEN_WIDTH * 0.5), 80
        header_rect = pygame.Rect(SCREEN_WIDTH // 2 - header_w // 2, 40, header_w, header_h)
        s = pygame.Surface((header_w, header_h), pygame.SRCALPHA)
        s.fill((249, 244, 227, 220))
        screen.blit(s, (header_rect.x, header_rect.y))
        pygame.draw.rect(screen, BLACK, header_rect, 3, border_radius=5)
        draw_text(screen, "DEGREE CONFERRED: C.S. COMPLETED!", SCREEN_WIDTH // 2, 69, medium_font, BLACK, True)

        btn_w, btn_h = 300, 60
        game.btn_exit_win = Button(
            "RETURN TO TITLE",
            SCREEN_WIDTH // 2 - btn_w // 2,
            SCREEN_HEIGHT - 100,
            btn_w, btn_h, OU_CREAM,
        )
        game.btn_exit_win.draw(screen, font)