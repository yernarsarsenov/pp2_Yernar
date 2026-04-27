import pygame
import math
import datetime

def flood_fill(surface, x, y, new_color):
    """Алгоритм заливки замкнутой области цветом."""
    try:
        target_color = surface.get_at((x, y))
    except IndexError:
        return
    if target_color == new_color:
        return
    
    pixels = [(x, y)]
    w, h = surface.get_size()
    while pixels:
        cx, cy = pixels.pop()
        if surface.get_at((cx, cy)) != target_color:
            continue
        surface.set_at((cx, cy), new_color)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h:
                pixels.append((nx, ny))

def get_shape_points(tool, start, end):
    """Рассчитывает координаты вершин для треугольников и ромба."""
    if tool == "right_tri":
        return [start, (end[0], start[1]), (start[0], end[1])]
    elif tool == "eq_tri":
        base = end[0] - start[0]
        height = abs(base) * math.sqrt(3) / 2
        direction = -1 if end[1] < start[1] else 1
        return [start, (end[0], start[1]), (start[0] + base // 2, int(start[1] + direction * height))]
    elif tool == "rhombus":
        x0, y0 = min(start[0], end[0]), min(start[1], end[1])
        x1, y1 = max(start[0], end[0]), max(start[1], end[1])
        mx, my = (x0 + x1) // 2, (y0 + y1) // 2
        return [(mx, y0), (x1, my), (mx, y1), (x0, my)]
    return []

def get_save_filename():
    """Создает уникальное имя файла с текущей датой и временем."""
    return datetime.datetime.now().strftime("paint_%Y-%m-%d_%H:%M:%S.png")