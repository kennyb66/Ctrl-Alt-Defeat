import pygame
from src.constants import *

def draw_text(screen, text, x, y, font, color=WHITE, center=False):
    """Renders text to the screen with an optional centering toggle."""
    img = font.render(text, True, color)
    if center:
        x -= img.get_width() // 2
    screen.blit(img, (x, y))

def wrap_text(text, font, max_width):
    """Wraps text to fit within a specific width (useful for bubbles/cards)."""
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines
class Button:
    def __init__(self, text, x, y, w, h, base_color, hover_color=OU_CREAM, disabled=False):
        self.text = text
        self.base_y = y  # Store base y for centering
        self.w = w
        self.base_color = base_color
        self.hover_color = hover_color
        self.disabled = disabled
        self.rect = pygame.Rect(x, y, w, h)  # Will be updated in draw()
        self.min_height = h
        
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width - 20:  # 20px padding
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def draw(self, screen, font):
        # Wrap text and calculate height
        lines = self.wrap_text(self.text, font, self.w)
        line_height = font.get_height()
        padding = 10
        calculated_height = max(self.min_height, len(lines) * line_height + padding * 2)
        
        # Center button vertically around base_y
        y = self.base_y - (calculated_height // 2)
        
        # Update rect
        self.rect = pygame.Rect(self.rect.x, y, self.w, calculated_height)
        
        # Determine color
        mouse_pos = pygame.mouse.get_pos()
        color = self.base_color
        if self.disabled:
            color = (30, 30, 30)  # Dark gray for disabled buttons
        elif self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        
        # Draw button
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
        
        # Draw text lines
        txt_color = BLACK if (color == self.hover_color and not self.disabled) else WHITE
        total_text_height = len(lines) * line_height
        start_y = self.rect.y + (self.rect.h - total_text_height) // 2
        
        for i, line in enumerate(lines):
            txt = font.render(line, True, txt_color)
            txt_x = self.rect.x + (self.rect.w - txt.get_width()) // 2
            txt_y = start_y + (i * line_height)
            screen.blit(txt, (txt_x, txt_y))
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and not self.disabled

def draw_speech_bubble(screen, text, x, y, font, width=350, type = "boss"):
    """Draws a speech bubble that scales based on the length of the text."""
    lines = wrap_text(text, font, width - 40)
    line_height = font.get_linesize()
    bubble_height = len(lines) * line_height + 40
    
    # Position bubble above/left of the professor
    bubble_rect = pygame.Rect(x - width, y - bubble_height - 30, width, bubble_height)
    
    # Draw bubble tail pointing to the boss sprite
    if type == "boss":
        pygame.draw.polygon(screen, WHITE, [
            (x - 40, y - 30), (x - 60, y - 30), (x - 20, y)
        ])
    else:
        pygame.draw.polygon(screen, WHITE, [
            (x + 40, y - 30), (x + 60, y - 30), (x + 20, y)
        ])

    
    # Draw bubble body
    pygame.draw.rect(screen, WHITE, bubble_rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, bubble_rect, 3, border_radius=15)
    
    for i, line in enumerate(lines):
        txt_img = font.render(line, True, BLACK)
        screen.blit(txt_img, (bubble_rect.x + 20, bubble_rect.y + 20 + (i * line_height)))