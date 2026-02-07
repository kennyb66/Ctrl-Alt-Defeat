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
        self.rect = pygame.Rect(x, y, w, h)
        self.base_color = base_color
        self.hover_color = hover_color
        self.disabled = disabled

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        color = self.base_color
        
        if self.disabled:
            color = (30, 30, 30) # Dark gray for disabled buttons
        elif self.rect.collidepoint(mouse_pos):
            color = self.hover_color

        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
        
        # Change text color to black if hovering (for contrast)
        txt_color = BLACK if (color == self.hover_color and not self.disabled) else WHITE
        txt = font.render(self.text, True, txt_color)
        screen.blit(txt, (self.rect.x + (self.rect.w - txt.get_width())//2, 
                          self.rect.y + (self.rect.h - txt.get_height())//2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and not self.disabled

def draw_speech_bubble(screen, text, x, y, font, width=350):
    """Draws a speech bubble that scales based on the length of the text."""
    lines = wrap_text(text, font, width - 40)
    line_height = font.get_linesize()
    bubble_height = len(lines) * line_height + 40
    
    # Position bubble above/left of the professor
    bubble_rect = pygame.Rect(x - width, y - bubble_height - 30, width, bubble_height)
    
    # Draw bubble tail pointing to the boss sprite
    pygame.draw.polygon(screen, WHITE, [
        (x - 40, y - 30), (x - 60, y - 30), (x - 20, y)
    ])
    
    # Draw bubble body
    pygame.draw.rect(screen, WHITE, bubble_rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, bubble_rect, 3, border_radius=15)
    
    for i, line in enumerate(lines):
        txt_img = font.render(line, True, BLACK)
        screen.blit(txt_img, (bubble_rect.x + 20, bubble_rect.y + 20 + (i * line_height)))