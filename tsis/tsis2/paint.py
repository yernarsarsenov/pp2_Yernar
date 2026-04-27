import pygame
import math
from tools import flood_fill, get_shape_points, get_save_filename

# --- НАСТРОЙКИ ИЗ ТВОЕГО ОРИГИНАЛА ---
SCREEN_W, SCREEN_H = 900, 650
TOOLBAR_W = 130
CANVAS_X, CANVAS_Y = TOOLBAR_W, 0
CANVAS_W, CANVAS_H = SCREEN_W - TOOLBAR_W, SCREEN_H

PALETTE = [
    (0,0,0), (255,255,255), (200,0,0), (0,180,0), (0,0,220), (255,165,0),
    (255,255,0), (128,0,128), (0,200,200), (255,20,147), (139,69,19), (128,128,128)
]

TOOLBAR_BG, TOOLBAR_BORDER = (45, 45, 45), (80, 80, 80)
SELECTED_BORDER = (255, 220, 0)
BTN_NORMAL, BTN_HOVER = (70, 70, 70), (100, 100, 100)
WHITE, BLACK = (255, 255, 255), (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Lvl Up Paint")
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)
font_ui = pygame.font.SysFont("Consolas", 12, bold=True)
font_canvas = pygame.font.SysFont("Arial", 24)

class Button:
    def __init__(self, rect, label, tool_id):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.tool_id = tool_id

    def draw(self, surface, selected, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        color = BTN_HOVER if hovered else BTN_NORMAL
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        border = SELECTED_BORDER if selected else TOOLBAR_BORDER
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=5)
        txt = font_ui.render(self.label, True, WHITE)
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

buttons = [
    Button((10, 10, 110, 30), "Pen", "pen"),
    Button((10, 45, 110, 30), "Line", "line"),
    Button((10, 80, 110, 30), "Eraser", "eraser"),
    Button((10, 115, 110, 30), "Fill", "fill"),
    Button((10, 150, 110, 30), "Text", "text"),
    Button((10, 185, 110, 30), "Rect", "rect"),
    Button((10, 220, 110, 30), "Circle", "circle"),
    Button((10, 255, 110, 30), "R.Tri", "right_tri"),
    Button((10, 290, 110, 30), "Eq.Tri", "eq_tri"),
    Button((10, 325, 110, 30), "Rhombus", "rhombus"),
    Button((10, 325, 110, 30), "Square", "square"),
]

# --- СОСТОЯНИЕ ---
current_tool = "pen"
current_color = BLACK
brush_radius = 2
dragging = False
drag_start = None
prev_pos = None
text_active = False
user_text = ""
text_pos = (0, 0)

def to_canvas(pos): return (pos[0] - TOOLBAR_W, pos[1])

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    m_on_canvas = mouse_pos[0] >= TOOLBAR_W

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if text_active:
                if event.key == pygame.K_RETURN:
                    canvas.blit(font_canvas.render(user_text, True, current_color), text_pos)
                    text_active = False
                elif event.key == pygame.K_ESCAPE: text_active = False
                elif event.key == pygame.K_BACKSPACE: user_text = user_text[:-1]
                else: user_text += event.unicode
            else:
                if event.key == pygame.K_1: brush_radius = 2
                if event.key == pygame.K_2: brush_radius = 5
                if event.key == pygame.K_3: brush_radius = 10
                if event.key == pygame.K_c: canvas.fill(WHITE)
                
                # Сохранение: Command+S (Mac) или Ctrl+S (Win)
                is_cmd_or_ctrl = pygame.key.get_mods() & (pygame.KMOD_META | pygame.KMOD_CTRL)
                if event.key == pygame.K_s and is_cmd_or_ctrl:
                    fname = get_save_filename()
                    pygame.image.save(canvas, fname)
                    print(f"Saved: {fname}")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if m_on_canvas:
                cp = to_canvas(mouse_pos)
                if current_tool == "fill": flood_fill(canvas, cp[0], cp[1], current_color)
                elif current_tool == "text": 
                    text_active, text_pos, user_text = True, cp, ""
                elif current_tool in ["pen", "eraser"]: prev_pos = cp
                else: dragging, drag_start = True, cp
            else:
                for btn in buttons:
                    if btn.rect.collidepoint(mouse_pos): current_tool = btn.tool_id
                for i, col in enumerate(PALETTE):
                    if pygame.Rect(10 + (i%4)*30, 400 + (i//4)*30, 25, 25).collidepoint(mouse_pos):
                        current_color = col

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging and m_on_canvas:
                cp = to_canvas(mouse_pos)
                if current_tool == "line": pygame.draw.line(canvas, current_color, drag_start, cp, brush_radius)
                elif current_tool == "square":
                    width = cp[0] - drag_start[0]
                    height = cp[1] - drag_start[1]
                    side = max(abs(width), abs(height))
                    s_x = side if width > 0 else -side
                    s_y = side if height > 0 else -side
                    
                    rect = pygame.Rect(drag_start[0], drag_start[1], s_x, s_y)
                    rect.normalize() # Исправляет отрицательные значения для корректной отрисовки
                    pygame.draw.rect(canvas, current_color, rect, brush_radius)
                    
                elif current_tool == "rect":
                    r = pygame.Rect(min(drag_start[0], cp[0]), min(drag_start[1], cp[1]), abs(cp[0]-drag_start[0]), abs(cp[1]-drag_start[1]))
                    pygame.draw.rect(canvas, current_color, r, brush_radius)
                elif current_tool == "circle":
                    rad = int(math.hypot(cp[0]-drag_start[0], cp[1]-drag_start[1]))
                    pygame.draw.circle(canvas, current_color, drag_start, rad, brush_radius)
                elif current_tool in ["right_tri", "eq_tri", "rhombus"]:
                    pts = get_shape_points(current_tool, drag_start, cp)
                    if pts: pygame.draw.polygon(canvas, current_color, pts, brush_radius)
            dragging, prev_pos = False, None

        if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0] and m_on_canvas:
            cp = to_canvas(mouse_pos)
            if current_tool == "pen" and prev_pos:
                pygame.draw.line(canvas, current_color, prev_pos, cp, brush_radius)
                prev_pos = cp
            elif current_tool == "eraser" and prev_pos:
                pygame.draw.line(canvas, WHITE, prev_pos, cp, brush_radius * 4)
                prev_pos = cp

    # --- ОТРИСОВКА ---
    screen.fill((30, 30, 30))
    screen.blit(canvas, (TOOLBAR_W, 0))

    if text_active:
        screen.blit(font_canvas.render(user_text + "|", True, current_color), (text_pos[0]+TOOLBAR_W, text_pos[1]))

    # Тулбар
    pygame.draw.rect(screen, TOOLBAR_BG, (0, 0, TOOLBAR_W, SCREEN_H))
    for btn in buttons: btn.draw(screen, btn.tool_id == current_tool, mouse_pos)
    for i, col in enumerate(PALETTE):
        r = pygame.Rect(10 + (i%4)*30, 400 + (i//4)*30, 25, 25)
        pygame.draw.rect(screen, col, r)
        if col == current_color: pygame.draw.rect(screen, SELECTED_BORDER, r, 2)

    screen.blit(font_ui.render(f"Size: {brush_radius}px", True, WHITE), (10, 580))
    pygame.display.flip()

pygame.quit()