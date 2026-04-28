import pygame
import math

def get_shape_points(mode, start, end):
    """Calculates vertex points or rects for various shapes."""
    x1, y1 = start
    x2, y2 = end
    
    if mode == "square":
        side = max(abs(x2 - x1), abs(y2 - y1))
        rect_x = x1 if x2 > x1 else x1 - side
        rect_y = y1 if y2 > y1 else y1 - side
        return [pygame.Rect(rect_x, rect_y, side, side)]
    
    elif mode == "r_triangle":
        # Right triangle: (x1, y1) to (x1, y2) to (x2, y2)
        return [(x1, y1), (x1, y2), (x2, y2)]
    
    elif mode == "e_triangle":
        # Equilateral-ish triangle: base on y2, apex at (x1, y1)
        height = (y2 - y1)
        base_half = abs(height) / math.sqrt(3)
        return [(x1, y1), (x1 - base_half, y2), (x1 + base_half, y2)]
    
    elif mode == "rhombus":
        # Rhombus centered in the bounding box
        mid_x = x1 + (x2 - x1) / 2
        mid_y = y1 + (y2 - y1) / 2
        return [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
    
    return []

def flood_fill(surface, x, y, new_color):
    """Stack-based flood fill algorithm."""
    target_color = surface.get_at((x, y))
    if target_color == new_color:
        return
    
    width, height = surface.get_size()
    stack = [(x, y)]
    
    while stack:
        curr_x, curr_y = stack.pop()
        
        if curr_x < 0 or curr_x >= width or curr_y < 0 or curr_y >= height:
            continue
        
        if surface.get_at((curr_x, curr_y)) == target_color:
            surface.set_at((curr_x, curr_y), new_color)
            stack.append((curr_x + 1, curr_y))
            stack.append((curr_x - 1, curr_y))
            stack.append((curr_x, curr_y + 1))
            stack.append((curr_x, curr_y - 1))
