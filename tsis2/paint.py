import pygame
import sys
import datetime
import os
import math
from tools import get_shape_points, flood_fill

pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 750
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Setup screen and canvas
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Extended Paint - TSIS 2")
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# State variables
current_color = BLACK
brush_sizes = {1: 2, 2: 5, 3: 10}
current_size = brush_sizes[2]
mode = "pencil"  # pencil, line, rect, circle, square, r_triangle, e_triangle, rhombus, fill, text
eraser = False
drawing = False
start_pos = None
last_pos = None

# Text tool state
text_pos = None
text_input = ""
is_typing = False

font = pygame.font.SysFont("Arial", 18)
ui_font = pygame.font.SysFont("Arial", 14)

def save_canvas():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"paint_{timestamp}.png"
    pygame.image.save(canvas, filename)
    print(f"Saved as {filename}")

def draw_ui():
    # Sidebar background
    pygame.draw.rect(screen, GRAY, (0, 0, 180, HEIGHT))
    pygame.draw.line(screen, BLACK, (180, 0), (180, HEIGHT), 2)

    # Color selection
    colors = [BLACK, RED, GREEN, BLUE, YELLOW, WHITE]
    for i, color in enumerate(colors):
        pygame.draw.rect(screen, color, (10 + (i % 2) * 80, 10 + (i // 2) * 50, 70, 40))
        if current_color == color and not eraser:
            pygame.draw.rect(screen, BLACK, (10 + (i % 2) * 80, 10 + (i // 2) * 50, 70, 40), 3)

    # Brush sizes
    y_offset = 170
    for key, size in brush_sizes.items():
        pygame.draw.rect(screen, WHITE, (10 + (key-1) * 55, y_offset, 50, 40))
        pygame.draw.circle(screen, BLACK, (35 + (key-1) * 55, y_offset + 20), size)
        if current_size == size:
            pygame.draw.rect(screen, BLUE, (10 + (key-1) * 55, y_offset, 50, 40), 2)
    
    # Modes
    modes = [
        ("Pencil", "pencil"), ("Line", "line"),
        ("Rect", "rect"), ("Circle", "circle"),
        ("Square", "square"), ("R-Tri", "r_triangle"),
        ("E-Tri", "e_triangle"), ("Rhombus", "rhombus"),
        ("Fill", "fill"), ("Text", "text"),
        ("Eraser", "eraser"), ("Clear", "clear")
    ]
    
    y_start = 230
    for i, (label, m) in enumerate(modes):
        rect = pygame.Rect(10 + (i % 2) * 85, y_start + (i // 2) * 45, 80, 40)
        pygame.draw.rect(screen, WHITE, rect)
        if mode == m or (m == "eraser" and eraser):
            pygame.draw.rect(screen, BLUE, rect, 2)
        txt = ui_font.render(label, True, BLACK)
        screen.blit(txt, (rect.x + 5, rect.y + 10))

def main():
    global current_color, current_size, mode, eraser, drawing, start_pos, last_pos, is_typing, text_input, text_pos
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        screen.fill(WHITE)
        screen.blit(canvas, (0, 0))
        draw_ui()
        
        curr_pos = pygame.mouse.get_pos()
        draw_color = WHITE if eraser else current_color
        
        # Live Preview
        if drawing and start_pos:
            if mode == "line":
                pygame.draw.line(screen, draw_color, start_pos, curr_pos, current_size)
            elif mode == "rect":
                r = pygame.Rect(start_pos, (curr_pos[0]-start_pos[0], curr_pos[1]-start_pos[1]))
                pygame.draw.rect(screen, draw_color, r, current_size)
            elif mode == "circle":
                radius = int(math.hypot(curr_pos[0]-start_pos[0], curr_pos[1]-start_pos[1]))
                pygame.draw.circle(screen, draw_color, start_pos, radius, current_size)
            elif mode in ["square", "r_triangle", "e_triangle", "rhombus"]:
                pts = get_shape_points(mode, start_pos, curr_pos)
                if mode == "square":
                    pygame.draw.rect(screen, draw_color, pts[0], current_size)
                else:
                    pygame.draw.polygon(screen, draw_color, pts, current_size)
        
        # Text Input Preview
        if is_typing and text_pos:
            txt_surf = font.render(text_input + "|", True, current_color)
            screen.blit(txt_surf, text_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if is_typing:
                    if event.key == pygame.K_RETURN:
                        txt_surf = font.render(text_input, True, current_color)
                        canvas.blit(txt_surf, text_pos)
                        is_typing = False
                        text_input = ""
                    elif event.key == pygame.K_ESCAPE:
                        is_typing = False
                        text_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    else:
                        text_input += event.unicode
                else:
                    if event.key == pygame.K_1: current_size = brush_sizes[1]
                    if event.key == pygame.K_2: current_size = brush_sizes[2]
                    if event.key == pygame.K_3: current_size = brush_sizes[3]
                    if (event.key == pygame.K_s) and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        save_canvas()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < 180: # UI Click
                    # Handle UI selections (omitted detailed collision for brevity, using simple checks)
                    if y < 160: # Colors
                        col = x // 80 + (y // 50) * 2
                        colors = [BLACK, RED, GREEN, BLUE, YELLOW, WHITE]
                        if col < len(colors):
                            current_color = colors[col]
                            eraser = False
                    elif y < 220: # Brush sizes
                        idx = (x - 10) // 55 + 1
                        if idx in brush_sizes: current_size = brush_sizes[idx]
                    else: # Modes
                        row = (y - 230) // 45
                        col = (x - 10) // 85
                        idx = row * 2 + col
                        modes_list = ["pencil", "line", "rect", "circle", "square", "r_triangle", "e_triangle", "rhombus", "fill", "text", "eraser", "clear"]
                        if 0 <= idx < len(modes_list):
                            m = modes_list[idx]
                            if m == "clear": canvas.fill(WHITE)
                            elif m == "eraser": eraser = True; mode = "pencil"
                            else: mode = m; eraser = False
                else: # Canvas Click
                    if mode == "fill":
                        flood_fill(canvas, x, y, current_color)
                    elif mode == "text":
                        is_typing = True
                        text_pos = (x, y)
                        text_input = ""
                    else:
                        drawing = True
                        start_pos = (x, y)
                        last_pos = (x, y)
            
            if event.type == pygame.MOUSEBUTTONUP:
                if drawing and start_pos:
                    end_pos = event.pos
                    if mode == "line":
                        pygame.draw.line(canvas, draw_color, start_pos, end_pos, current_size)
                    elif mode == "rect":
                        r = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                        pygame.draw.rect(canvas, draw_color, r, current_size)
                    elif mode == "circle":
                        radius = int(math.hypot(end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                        pygame.draw.circle(canvas, draw_color, start_pos, radius, current_size)
                    elif mode in ["square", "r_triangle", "e_triangle", "rhombus"]:
                        pts = get_shape_points(mode, start_pos, end_pos)
                        if mode == "square":
                            pygame.draw.rect(canvas, draw_color, pts[0], current_size)
                        else:
                            pygame.draw.polygon(canvas, draw_color, pts, current_size)
                drawing = False
                start_pos = None

            if event.type == pygame.MOUSEMOTION and drawing:
                if mode == "pencil":
                    pygame.draw.line(canvas, draw_color, last_pos, event.pos, current_size)
                    last_pos = event.pos
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
