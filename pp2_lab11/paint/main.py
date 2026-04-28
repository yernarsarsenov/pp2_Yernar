import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Extended Paint - Lab 11")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

colors = [BLACK, RED, GREEN, BLUE, YELLOW]
current_color = BLACK

brush_sizes = [4, 8, 16]
current_size = brush_sizes[0]

eraser = False
mode = "brush"  # brush, rect, circle, square, r_triangle, e_triangle, rhombus

drawing = False
start_pos = None

# Canvas to draw on
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

font = pygame.font.SysFont(None, 20)

def draw_ui():
    """Draws the sidebar UI with tool and color selections."""
    # Color buttons
    for i, color in enumerate(colors):
        pygame.draw.rect(screen, color, (10 + i*45, 10, 40, 40))    

    # Brush size buttons
    for i, size in enumerate(brush_sizes):
        pygame.draw.rect(screen, BLACK, (10 + i*45, 60, 40, 40), 1) 
        pygame.draw.circle(screen, BLACK, (30 + i*45, 80), size)    

    # Mode buttons configuration
    modes = [
        ("Eraser", (10, 110), "eraser"),
        ("Clear", (10, 160), "clear"),
        ("Rect", (10, 210), "rect"),
        ("Circle", (10, 260), "circle"),
        ("Square", (10, 310), "square"),
        ("R-Triangle", (10, 360), "r_triangle"),
        ("E-Triangle", (10, 410), "e_triangle"),
        ("Rhombus", (10, 460), "rhombus")
    ]

    for text, pos, m in modes:
        pygame.draw.rect(screen, (220, 220, 220), (pos[0], pos[1], 100, 40))
        txt_surface = font.render(text, True, BLACK)
        screen.blit(txt_surface, (pos[0] + 5, pos[1] + 12))

def get_shape_points(mode, start, end):
    """Calculates vertex points for various shapes."""
    x1, y1 = start
    x2, y2 = end
    
    if mode == "square":
        side = max(abs(x2 - x1), abs(y2 - y1))
        rect_x = x1 if x2 > x1 else x1 - side
        rect_y = y1 if y2 > y1 else y1 - side
        return [pygame.Rect(rect_x, rect_y, side, side)]
    
    elif mode == "r_triangle":
        return [(x1, y1), (x1, y2), (x2, y2)]
    
    elif mode == "e_triangle":
        height = (y2 - y1)
        base_half = abs(height) / math.sqrt(3)
        return [(x1, y1), (x1 - base_half, y2), (x1 + base_half, y2)]
    
    elif mode == "rhombus":
        return [(x1, y1 + (y2-y1)/2), (x1 + (x2-x1)/2, y1), (x2, y1 + (y2-y1)/2), (x1 + (x2-x1)/2, y2)]
    
    return []

running = True
last_pos = None

while running:
    screen.fill(WHITE)
    screen.blit(canvas, (0, 0))
    draw_ui()

    current_pos = pygame.mouse.get_pos()
    color = WHITE if eraser else current_color

    # Preview logic
    if drawing and start_pos:
        if mode == "rect":
            rect = pygame.Rect(start_pos, (current_pos[0]-start_pos[0], current_pos[1]-start_pos[1]))
            pygame.draw.rect(screen, color, rect, current_size)
        elif mode == "circle":
            radius = int(((current_pos[0]-start_pos[0])**2 + (current_pos[1]-start_pos[1])**2)**0.5)
            pygame.draw.circle(screen, color, start_pos, radius, current_size)
        elif mode in ["square", "r_triangle", "e_triangle", "rhombus"]:
            pts = get_shape_points(mode, start_pos, current_pos)
            if mode == "square":
                pygame.draw.rect(screen, color, pts[0], current_size)
            else:
                pygame.draw.polygon(screen, color, pts, current_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if x < 250: # UI Interaction
                for i, c in enumerate(colors):
                    if pygame.Rect(10 + i*45, 10, 40, 40).collidepoint(x, y):
                        current_color = c; eraser = False; mode = "brush"
                for i, s in enumerate(brush_sizes):
                    if pygame.Rect(10 + i*45, 60, 40, 40).collidepoint(x, y):
                        current_size = s
                
                # Check mode buttons
                if pygame.Rect(10, 110, 100, 40).collidepoint(x, y): eraser = True; mode = "brush"
                if pygame.Rect(10, 160, 100, 40).collidepoint(x, y): canvas.fill(WHITE)
                if pygame.Rect(10, 210, 100, 40).collidepoint(x, y): mode = "rect"; eraser = False
                if pygame.Rect(10, 260, 100, 40).collidepoint(x, y): mode = "circle"; eraser = False
                if pygame.Rect(10, 310, 100, 40).collidepoint(x, y): mode = "square"; eraser = False
                if pygame.Rect(10, 360, 100, 40).collidepoint(x, y): mode = "r_triangle"; eraser = False
                if pygame.Rect(10, 410, 100, 40).collidepoint(x, y): mode = "e_triangle"; eraser = False
                if pygame.Rect(10, 460, 100, 40).collidepoint(x, y): mode = "rhombus"; eraser = False
            
            drawing = True
            start_pos = event.pos
            last_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing and start_pos:
                end_pos = event.pos
                if mode == "rect":
                    rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    pygame.draw.rect(canvas, color, rect, current_size)
                elif mode == "circle":
                    radius = int(((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)**0.5)
                    pygame.draw.circle(canvas, color, start_pos, radius, current_size)
                elif mode in ["square", "r_triangle", "e_triangle", "rhombus"]:
                    pts = get_shape_points(mode, start_pos, end_pos)
                    if mode == "square":
                        pygame.draw.rect(canvas, color, pts[0], current_size)
                    else:
                        pygame.draw.polygon(canvas, color, pts, current_size)
            drawing = False

        elif event.type == pygame.MOUSEMOTION and drawing:
            if mode == "brush":
                pygame.draw.line(canvas, color, last_pos, event.pos, current_size)
                last_pos = event.pos

    pygame.display.flip()

pygame.quit()
sys.exit()
