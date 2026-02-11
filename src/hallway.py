import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WALK, IDLE, DOOR_VIEW, MENU


class HallwayManager:
    def update(self, game) -> None:
        if game.victory_stage > 0:
            game.player.update()
            return

        if not game.show_exit_prompt:
            self._handle_movement(game)
            self._handle_door_interact(game)
        else:
            game.player.set_state(IDLE)

        self._clamp_and_track_camera(game)
        game.player.update()

    def _handle_movement(self, game) -> None:
        keys = pygame.key.get_pressed()
        speed = 10

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            game.player_world_x -= speed
            game.player.facing = "left"
            game.player.set_state(WALK)
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            game.player_world_x += speed
            game.player.facing = "right"
            game.player.set_state(WALK)
        else:
            game.player.set_state(IDLE)

    def _handle_door_interact(self, game) -> None:
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_e]:
            return
        for door in game.door_locations:
            distance = abs(game.player_world_x - door["x"])
            is_near = distance < game.door_interact_dist
            is_unlocked = door["level"] <= game.current_level
            if is_near and is_unlocked:
                game.selected_door = door
                game.state = DOOR_VIEW
                break

    def _clamp_and_track_camera(self, game) -> None:
        max_world_x = game.door_locations[-1]["x"] + 300
        game.player_world_x = max(100, min(game.player_world_x, max_world_x))

        target_camera_x = game.player_world_x - (SCREEN_WIDTH // 2)
        game.camera_x = max(0, min(target_camera_x, game.hallway_width - SCREEN_WIDTH))

        game.player_screen_x = game.player_world_x - game.camera_x

        if game.player_world_x <= 100:
            game.show_exit_prompt = True