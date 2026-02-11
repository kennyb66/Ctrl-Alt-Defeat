import pygame
import os
from src.constants import BLACK, GOLD, GRAY


class AssetLoader:
    def __init__(self, screen: pygame.Surface, base_dir: str):
        self.screen = screen
        self.base_dir = base_dir

        w = screen.get_width()
        h = screen.get_height()

        self.fonts = self._load_fonts(h)
        self.scroll_bg = self._load_scroll_bg(w, h)
        self.ui_scroll = self._load_ui_scroll()
        self.custom_cursor, self.cursor_visible = self._load_cursor()
        self.notebook_paper_img = self._load_notebook_paper()
        self.hallway_start, self.hallway_loop, self.loop_w, self.mid_point = self._load_hallway(w, h)
        self.background_assets = self._load_named_backgrounds(w, h)
        self.battle_backgrounds = self._load_battle_backgrounds(w, h)
        self.door_img, self.door_upclose_img, self.door_nametage_img = self._load_door_assets(w, h)
        self.floor_textures = self._load_floor_textures(w)

    def _load_fonts(self, screen_h: int) -> dict:
        return {
            "normal": pygame.font.SysFont("Courier", int(screen_h * 0.025)),
            "title": pygame.font.SysFont("Courier", int(screen_h * 0.07), bold=True),
            "medium":pygame.font.SysFont("Courier", int(screen_h * 0.035), bold=True),
            "small": pygame.font.SysFont("Courier", int(screen_h * 0.02)),
        }

    def _load_scroll_bg(self, w: int, h: int) -> pygame.Surface:
        path = os.path.join(self.base_dir, "assets", "backgrounds", "scroll.png")
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (int(w * 0.85), int(h * 0.65)))

    def _load_ui_scroll(self) -> pygame.Surface:
        path = os.path.join(self.base_dir, "assets", "backgrounds", "scroll.png")
        return pygame.image.load(path).convert_alpha()

    def _load_cursor(self) -> tuple:
        path = os.path.join(self.base_dir, "assets", "ui", "mouse cursor.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (32, 32))
                img = img.convert_alpha()
                pygame.mouse.set_visible(False)
                return img, True
            except Exception as e:
                print(f"Error loading cursor: {e}")
        return None, False

    def _load_notebook_paper(self) -> pygame.Surface | None:
        path = os.path.join(self.base_dir, "assets", "ui", "notebook_paper.webp")
        if os.path.exists(path):
            try:
                return pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Error loading notebook paper: {e}")
        return None

    def _load_hallway(self, screen_w: int, screen_h: int):
        path = os.path.join(self.base_dir, "assets", "backgrounds", "hallway.png")
        try:
            raw = pygame.image.load(path).convert()
            scale = screen_h / raw.get_height()
            tex = pygame.transform.scale(raw, (int(raw.get_width() * scale), screen_h))
        except Exception:
            tex = pygame.Surface((screen_w, screen_h))
            tex.fill((30, 30, 35))

        full_w = tex.get_width()
        mid = full_w // 2
        start = tex.subsurface((0, 0, mid, screen_h))
        loop = tex.subsurface((mid, 0, mid, screen_h))
        return start, loop, loop.get_width(), mid

    def _load_named_backgrounds(self, w: int, h: int) -> dict:
        names = ["title", "lost_sridhar", "lost_maiti", "lost_dioch",
                 "class", "win_kris", "win_shri", "win_ken", "end"]
        assets = {}
        for name in names:
            path = os.path.join(self.base_dir, "assets", "backgrounds", f"{name}.png")
            try:
                img = pygame.image.load(path).convert()
                assets[name] = pygame.transform.scale(img, (w, h))
            except Exception:
                fallback = pygame.Surface((w, h))
                fallback.fill(BLACK)
                assets[name] = fallback
        return assets

    def _load_battle_backgrounds(self, screen_w: int, screen_h: int) -> list:
        bgs = []
        try:
            for i in range(1, 4):
                path = os.path.join(self.base_dir, "assets", "backgrounds", f"battle_bg_{i}.png")
                raw = pygame.image.load(path).convert()
                orig_w, orig_h = raw.get_size()
                scale = max(screen_w / orig_w, screen_h / orig_h)
                new_w, new_h = int(orig_w * scale), int(orig_h * scale)
                raw = pygame.transform.smoothscale(raw, (new_w, new_h))
                x_off = (screen_w - new_w) // 2
                y_off = (screen_h - new_h) // 2
                final = pygame.Surface((screen_w, screen_h))
                final.fill((0, 0, 0))
                final.blit(raw, (x_off, y_off))
                bgs.append(final)
        except Exception as e:
            print(f"Error loading battle backgrounds: {e}")
            colors = [(40, 30, 50), (30, 40, 60), (50, 30, 30)]
            bgs = []
            for c in colors:
                s = pygame.Surface((screen_w, screen_h))
                s.fill(c)
                bgs.append(s)
        return bgs

    def _load_door_assets(self, screen_w: int, screen_h: int):
        door_w = int(screen_w * 0.15)
        door_h = int(screen_h * 0.38)
        try:
            door_img = pygame.image.load(
                os.path.join(self.base_dir, "assets", "door.png")).convert_alpha()
            door_upclose_img = pygame.image.load(
                os.path.join(self.base_dir, "assets", "door_cracked.png")).convert_alpha()
            door_nametage_img = pygame.image.load(
                os.path.join(self.base_dir, "assets", "door_upclose.png")).convert_alpha()

            door_nametage_img = pygame.transform.scale(door_nametage_img, (screen_w, screen_h))
            door_img = pygame.transform.scale(door_img, (door_w, door_h))
            door_upclose_img = pygame.transform.scale(door_upclose_img, (screen_w, screen_h))
        except Exception:
            door_img = pygame.Surface((door_w, door_h))
            door_img.fill(GOLD)
            door_upclose_img = pygame.Surface((screen_w, screen_h))
            door_upclose_img.fill(GRAY)
            door_nametage_img = door_upclose_img

        return door_img, door_upclose_img, door_nametage_img

    def _load_floor_textures(self, screen_w: int) -> dict:
        specs = {
            1: ("grass.png",(34, 139, 34, 200)),
            2: ("navy.png", (0, 0, 128, 200)),
            3: ("tile.png", (48, 25, 52, 200)),
        }
        textures = {}
        for boss_id, (filename, fallback_color) in specs.items():
            path = os.path.join(self.base_dir, "assets", "backgrounds", filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                textures[boss_id] = img# scaled at draw time (height varies)
            except Exception:
                surf = pygame.Surface((screen_w, 1), pygame.SRCALPHA)
                surf.fill(fallback_color)
                textures[boss_id] = surf
        return textures