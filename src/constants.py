import pygame

pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
OU_CRIMSON = (132, 22, 23)
OU_CREAM = (241, 235, 210)
GRAY = (50, 50, 50)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)

MENU, SELECT, HALLWAY, DOOR_VIEW, BATTLE, WIN, LOSS, TOTAL_WIN = "MENU", "SELECT", "HALLWAY", "DOOR_VIEW", "BATTLE", "WIN", "LOSS", "TOTAL WIN"
IDLE, ACTION, WALK = "IDLE", "ACTION", "WALK"