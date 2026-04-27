# ================================================================
#  main.py — Screens, rendering, main loop
# ================================================================
import pygame
import sys
from pygame.locals import *

import settings as settings_mod
import db
from config import *
from game import (
    new_game_state, step, food_time_left_ms,
    border_walls, safe_start
)

# ── Init ────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake – TSIS 4")
clock = pygame.time.Clock()

font_hud    = pygame.font.SysFont("Consolas", 18, bold=True)
font_large  = pygame.font.SysFont("Consolas", 42, bold=True)
font_medium = pygame.font.SysFont("Consolas", 26, bold=True)
font_small  = pygame.font.SysFont("Consolas", 18)
font_pts    = pygame.font.SysFont("Consolas", 11, bold=True)

DB_OK = db.init_db()


# ================================================================
#  Drawing helpers
# ================================================================

def draw_cell(surface, col, row, color, shrink=2):
    rect = pygame.Rect(
        col * CELL + shrink,
        row * CELL + HUD_HEIGHT + shrink,
        CELL - shrink * 2,
        CELL - shrink * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=3)


def draw_text(surface, text, font, color, x, y):
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))
    return surf.get_width()


def draw_text_center(surface, text, font, color, y):
    surf = font.render(text, True, color)
    surface.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))


def draw_button(surface, text, rect, hovered):
    color = (80, 80, 80) if hovered else (50, 50, 50)
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, LIGHT_GRAY, rect, 2, border_radius=8)
    surf = font_medium.render(text, True, WHITE)
    surface.blit(surf, (
        rect.centerx - surf.get_width() // 2,
        rect.centery - surf.get_height() // 2
    ))


def draw_walls(surface, walls):
    border = border_walls()
    for (c, r) in walls:
        color = LIGHT_GRAY if (c, r) in border else DARK_GRAY
        draw_cell(surface, c, r, color, shrink=1)


def draw_obstacles(surface, obstacles):
    for (c, r) in obstacles:
        draw_cell(surface, c, r, OBSTACLE_COLOR, shrink=1)


def draw_snake(surface, snake, color, color_dark):
    for i, (c, r) in enumerate(snake):
        draw_cell(surface, c, r, color if i == 0 else color_dark)


def draw_food(surface, food):
    if food is None:
        return
    col, row = food["pos"]
    cx = col * CELL + CELL // 2
    cy = row * CELL + HUD_HEIGHT + CELL // 2
    radius = CELL // 2 - 2
    pygame.draw.circle(surface, food["ftype"]["color"], (cx, cy), radius)
    r, g, b = food["ftype"]["color"]
    pygame.draw.circle(surface, (max(0, r - 60), max(0, g - 60), max(0, b - 60)), (cx, cy), radius, 2)

    lifetime  = food["ftype"]["lifetime"] * 1000
    tl        = food_time_left_ms(food, pygame.time.get_ticks())
    ratio     = tl / lifetime
    bar_w     = CELL - 4
    bar_h     = 3
    bar_x     = col * CELL + 2
    bar_y     = (row + 1) * CELL + HUD_HEIGHT - bar_h - 1
    pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
    fw = int(bar_w * ratio)
    if fw > 0:
        if ratio > 0.5:
            t  = (ratio - 0.5) / 0.5
            bc = (int(255 * (1 - t)), 220, 0)
        else:
            t  = ratio / 0.5
            bc = (255, int(200 * t), 0)
        pygame.draw.rect(surface, bc, (bar_x, bar_y, fw, bar_h))

    pts = font_pts.render(f"+{food['ftype']['points']}", True, food["ftype"]["color"])
    surface.blit(pts, (col * CELL + CELL, row * CELL + HUD_HEIGHT))


def draw_poison(surface, poison):
    if poison is None:
        return
    col, row = poison["pos"]
    cx = col * CELL + CELL // 2
    cy = row * CELL + HUD_HEIGHT + CELL // 2
    radius = CELL // 2 - 2
    pygame.draw.circle(surface, DARK_RED, (cx, cy), radius)
    pygame.draw.circle(surface, (200, 0, 0), (cx, cy), radius, 2)
    pts = font_pts.render("-2", True, RED)
    surface.blit(pts, (col * CELL + CELL, row * CELL + HUD_HEIGHT))


def draw_powerup(surface, powerup):
    if powerup is None:
        return
    col, row = powerup["pos"]
    cx = col * CELL + CELL // 2
    cy = row * CELL + HUD_HEIGHT + CELL // 2
    radius = CELL // 2 - 1
    color  = powerup["ptype"]["color"]
    # Pulsing border
    t = (pygame.time.get_ticks() % 1000) / 1000.0
    pulse = int(3 + 2 * abs(t - 0.5) * 2)
    pygame.draw.circle(surface, color, (cx, cy), radius)
    pygame.draw.circle(surface, WHITE, (cx, cy), radius, pulse)

    # remaining time bar
    now     = pygame.time.get_ticks()
    elapsed = now - powerup["spawned_ms"]
    ratio   = max(0, 1 - elapsed / POWERUP_FIELD_LIFETIME)
    bar_w   = CELL - 4
    bar_h   = 3
    bar_x   = col * CELL + 2
    bar_y   = (row + 1) * CELL + HUD_HEIGHT - bar_h - 1
    pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
    fw = int(bar_w * ratio)
    if fw > 0:
        pygame.draw.rect(surface, color, (bar_x, bar_y, fw, bar_h))


def draw_grid(surface):
    for c in range(COLS):
        pygame.draw.line(surface, (30, 30, 30),
                         (c * CELL, HUD_HEIGHT), (c * CELL, SCREEN_H))
    for r in range(ROWS):
        pygame.draw.line(surface, (30, 30, 30),
                         (0, HUD_HEIGHT + r * CELL), (SCREEN_W, HUD_HEIGHT + r * CELL))


def draw_hud(surface, state, personal_best):
    surface.fill(GRAY, (0, 0, SCREEN_W, HUD_HEIGHT))
    x = 8
    draw_text(surface, f"Score:{state['score']}", font_hud, WHITE, x, 4)

    # personal best
    if personal_best is not None:
        pb_str = f"PB:{personal_best}"
        draw_text(surface, pb_str, font_hud, GOLD, x, 24)

    # food progress
    prog = f"Food:{state['foods_eaten']}/{FOODS_PER_LEVEL}"
    ps   = font_hud.render(prog, True, ORANGE)
    surface.blit(ps, (SCREEN_W // 2 - ps.get_width() // 2, 4))

    # level
    ls = font_hud.render(f"Level:{state['level']}", True, GOLD)
    surface.blit(ls, (SCREEN_W - ls.get_width() - 8, 4))

    # active power-up indicator
    ap = state["active_powerup"]
    if ap:
        now       = pygame.time.get_ticks()
        label     = ap["label"]
        if ap["name"] != "shield":
            remaining = max(0, state["powerup_end_ms"] - now) // 1000
            label     = f"{ap['label']} {remaining}s"
        aps = font_hud.render(label, True, ap["color"])
        surface.blit(aps, (SCREEN_W - aps.get_width() - 8, 24))

    # shield icon
    if state["shield_active"]:
        sh = font_hud.render("SHIELD", True, PURPLE)
        surface.blit(sh, (SCREEN_W // 2 - sh.get_width() // 2, 24))


def draw_overlay(surface, lines, colors=None, sub_lines=None, sub_colors=None):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 180))
    surface.blit(ov, (0, 0))
    total_h = len(lines) * 56 + (len(sub_lines) * 32 if sub_lines else 0)
    start_y = (SCREEN_H - total_h) // 2
    for i, line in enumerate(lines):
        color = colors[i] if colors and i < len(colors) else WHITE
        surf  = font_large.render(line, True, color)
        surface.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, start_y + i * 56))
    if sub_lines:
        sy = start_y + len(lines) * 56
        for i, line in enumerate(sub_lines):
            color = sub_colors[i] if sub_colors and i < len(sub_colors) else LIGHT_GRAY
            surf  = font_small.render(line, True, color)
            surface.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, sy + i * 32))


# ================================================================
#  Screen: Main Menu
# ================================================================

def screen_main_menu(sett: dict, personal_best_holder: list) -> tuple[str, str]:
    """Returns (action, username).
    action: 'play' | 'leaderboard' | 'settings' | 'quit'
    """
    username    = ""
    typing      = True
    btn_w, btn_h = 220, 44
    btn_x        = SCREEN_W // 2 - btn_w // 2

    buttons = {
        "play":        pygame.Rect(btn_x, 340, btn_w, btn_h),
        "leaderboard": pygame.Rect(btn_x, 396, btn_w, btn_h),
        "settings":    pygame.Rect(btn_x, 452, btn_w, btn_h),
        "quit":        pygame.Rect(btn_x, 508, btn_w, btn_h),
    }
    input_rect = pygame.Rect(SCREEN_W // 2 - 120, 260, 240, 44)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and typing:
                if event.key == K_BACKSPACE:
                    username = username[:-1]
                elif event.key == K_RETURN:
                    if username.strip():
                        typing = False
                elif len(username) < 20 and event.unicode.isprintable():
                    username += event.unicode
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for action, rect in buttons.items():
                    if rect.collidepoint(mouse_pos):
                        name = username.strip() or "Player"
                        if action == "play":
                            return action, name
                        return action, name

        screen.fill(BLACK)
        draw_text_center(screen, "SNAKE", font_large, GREEN, 60)
        draw_text_center(screen, "TSIS 4 Edition", font_small, LIGHT_GRAY, 118)

        # Username input
        draw_text_center(screen, "Enter username:", font_small, LIGHT_GRAY, 230)
        border_color = GOLD if typing else LIGHT_GRAY
        pygame.draw.rect(screen, DARK_GRAY, input_rect, border_radius=6)
        pygame.draw.rect(screen, border_color, input_rect, 2, border_radius=6)
        display_name = username + ("|" if typing and (pygame.time.get_ticks() // 500) % 2 == 0 else "")
        name_surf    = font_medium.render(display_name, True, WHITE)
        screen.blit(name_surf, (input_rect.x + 8, input_rect.y + 8))

        for action, rect in buttons.items():
            hovered = rect.collidepoint(mouse_pos)
            label   = {"play": "▶  Play", "leaderboard": "🏆 Leaderboard",
                       "settings": "⚙  Settings", "quit": "✕  Quit"}[action]
            draw_button(screen, label, rect, hovered)

        if not DB_OK:
            draw_text_center(screen, "⚠ DB offline — scores won't be saved", font_small, RED, SCREEN_H - 28)

        pygame.display.flip()
        clock.tick(30)


# ================================================================
#  Screen: Game Over
# ================================================================

def screen_game_over(score: int, level: int, personal_best) -> str:
    """Returns 'retry' or 'menu'."""
    btn_w, btn_h = 200, 44
    buttons = {
        "retry": pygame.Rect(SCREEN_W // 2 - btn_w - 10, SCREEN_H // 2 + 80, btn_w, btn_h),
        "menu":  pygame.Rect(SCREEN_W // 2 + 10,         SCREEN_H // 2 + 80, btn_w, btn_h),
    }

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for action, rect in buttons.items():
                    if rect.collidepoint(mouse_pos):
                        return action
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return "retry"
                if event.key == K_ESCAPE:
                    return "menu"

        screen.fill(BLACK)
        draw_text_center(screen, "GAME OVER", font_large, RED, SCREEN_H // 2 - 140)
        draw_text_center(screen, f"Score: {score}", font_medium, WHITE, SCREEN_H // 2 - 70)
        draw_text_center(screen, f"Level reached: {level}", font_medium, LIGHT_GRAY, SCREEN_H // 2 - 30)
        if personal_best is not None:
            pb_color = GOLD if score >= personal_best else LIGHT_GRAY
            pb_label = "NEW BEST!" if score >= personal_best else f"Personal best: {personal_best}"
            draw_text_center(screen, pb_label, font_medium, pb_color, SCREEN_H // 2 + 14)

        for action, rect in buttons.items():
            hovered = rect.collidepoint(mouse_pos)
            label   = "▶ Retry" if action == "retry" else "↩ Menu"
            draw_button(screen, label, rect, hovered)

        pygame.display.flip()
        clock.tick(30)


# ================================================================
#  Screen: Leaderboard
# ================================================================

def screen_leaderboard():
    rows      = db.get_leaderboard(10)
    back_rect = pygame.Rect(SCREEN_W // 2 - 100, SCREEN_H - 60, 200, 40)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mouse_pos):
                    return
            if event.type == KEYDOWN and event.key in (K_ESCAPE, K_RETURN):
                return

        screen.fill(BLACK)
        draw_text_center(screen, "🏆 LEADERBOARD", font_large, GOLD, 20)

        if not DB_OK or not rows:
            draw_text_center(screen, "No records yet." if DB_OK else "Database offline.", font_medium, LIGHT_GRAY, 120)
        else:
            headers = ["#", "Player", "Score", "Level", "Date"]
            xs      = [20, 60, 230, 320, 410]
            header_y = 88
            for i, h in enumerate(headers):
                draw_text(screen, h, font_small, GOLD, xs[i], header_y)
            pygame.draw.line(screen, LIGHT_GRAY, (10, 110), (SCREEN_W - 10, 110), 1)

            for rank, row in enumerate(rows, 1):
                y     = 118 + (rank - 1) * 34
                color = GOLD if rank == 1 else (SILVER if rank == 2 else (ORANGE if rank == 3 else WHITE))
                vals  = [
                    str(rank),
                    str(row.get("username", "?"))[:14],
                    str(row.get("score", 0)),
                    str(row.get("level_reached", 1)),
                    str(row.get("played_date", ""))[:10],
                ]
                for i, v in enumerate(vals):
                    draw_text(screen, v, font_small, color, xs[i], y)

        hovered = back_rect.collidepoint(mouse_pos)
        draw_button(screen, "← Back", back_rect, hovered)
        pygame.display.flip()
        clock.tick(30)


# ================================================================
#  Screen: Settings
# ================================================================

def screen_settings(sett: dict) -> dict:
    COLORS = [
        ("Green",  [0, 200, 0]),
        ("Blue",   [30, 100, 255]),
        ("Yellow", [255, 240, 0]),
        ("Orange", [255, 140, 0]),
        ("Cyan",   [0, 220, 220]),
        ("Purple", [180, 0, 220]),
        ("White",  [255, 255, 255]),
    ]
    # Find current color index
    cur_color_idx = 0
    for i, (_, rgb) in enumerate(COLORS):
        if list(sett["snake_color"]) == rgb:
            cur_color_idx = i
            break

    btn_w  = 200
    save_rect = pygame.Rect(SCREEN_W // 2 - btn_w // 2, SCREEN_H - 70, btn_w, 44)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                settings_mod.save(sett)
                return sett
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Grid toggle
                grid_rect = pygame.Rect(SCREEN_W // 2 - 60, 200, 120, 36)
                if grid_rect.collidepoint(mouse_pos):
                    sett["grid"] = not sett["grid"]
                # Sound toggle
                sound_rect = pygame.Rect(SCREEN_W // 2 - 60, 270, 120, 36)
                if sound_rect.collidepoint(mouse_pos):
                    sett["sound"] = not sett["sound"]
                # Color buttons
                for ci, (cname, crgb) in enumerate(COLORS):
                    cx_  = 50 + ci * 76
                    crect = pygame.Rect(cx_, 360, 64, 36)
                    if crect.collidepoint(mouse_pos):
                        cur_color_idx     = ci
                        sett["snake_color"] = crgb
                # Save & back
                if save_rect.collidepoint(mouse_pos):
                    settings_mod.save(sett)
                    return sett

        screen.fill(BLACK)
        draw_text_center(screen, "⚙ SETTINGS", font_large, WHITE, 30)

        # Grid
        draw_text_center(screen, "Grid overlay:", font_small, LIGHT_GRAY, 170)
        grid_rect  = pygame.Rect(SCREEN_W // 2 - 60, 200, 120, 36)
        grid_color = GREEN if sett["grid"] else DARK_GRAY
        pygame.draw.rect(screen, grid_color, grid_rect, border_radius=6)
        pygame.draw.rect(screen, LIGHT_GRAY, grid_rect, 2, border_radius=6)
        draw_text_center(screen, "ON" if sett["grid"] else "OFF", font_medium, WHITE, 204)

        # Sound
        draw_text_center(screen, "Sound:", font_small, LIGHT_GRAY, 240)
        sound_rect  = pygame.Rect(SCREEN_W // 2 - 60, 270, 120, 36)
        sound_color = GREEN if sett["sound"] else DARK_GRAY
        pygame.draw.rect(screen, sound_color, sound_rect, border_radius=6)
        pygame.draw.rect(screen, LIGHT_GRAY, sound_rect, 2, border_radius=6)
        draw_text_center(screen, "ON" if sett["sound"] else "OFF", font_medium, WHITE, 274)

        # Snake color
        draw_text_center(screen, "Snake color:", font_small, LIGHT_GRAY, 330)
        for ci, (cname, crgb) in enumerate(COLORS):
            cx_   = 50 + ci * 76
            crect = pygame.Rect(cx_, 360, 64, 36)
            pygame.draw.rect(screen, tuple(crgb), crect, border_radius=6)
            border = WHITE if ci == cur_color_idx else DARK_GRAY
            pygame.draw.rect(screen, border, crect, 3, border_radius=6)
            name_s = font_pts.render(cname, True, WHITE)
            screen.blit(name_s, (cx_ + 32 - name_s.get_width() // 2, 400))

        hovered = save_rect.collidepoint(mouse_pos)
        draw_button(screen, "💾 Save & Back", save_rect, hovered)
        pygame.display.flip()
        clock.tick(30)


# ================================================================
#  Screen: Level Clear transition
# ================================================================

def screen_level_clear(level_done: int, next_level: int, score: int) -> None:
    deadline = pygame.time.get_ticks() + 3000
    while True:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key in (K_RETURN, K_SPACE):
                return
        if now >= deadline:
            return

        left = max(0, deadline - now) / 1000
        draw_overlay(screen,
            ["LEVEL CLEAR!"],
            [GREEN],
            [f"Level {level_done} complete", f"Score: {score}",
             f"→ Level {next_level}",  f"ENTER  ({left:.1f}s)"],
            [LIGHT_GRAY, WHITE, GOLD, LIGHT_GRAY],
        )
        pygame.display.flip()
        clock.tick(30)


# ================================================================
#  Main gameplay loop
# ================================================================

def play_game(username: str, sett: dict) -> tuple[int, int]:
    """Run one full game. Returns (final_score, final_level)."""
    personal_best = db.get_personal_best(username)
    level         = 1
    score         = 0

    while True:
        state = new_game_state(level, score, sett)

        # Inner loop: one level
        result = ""
        while result not in ("dead", "level_done"):
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                if event.type == KEYDOWN:
                    d = state["direction"]
                    if event.key in (K_UP,    K_w) and d != DOWN:
                        state["next_dir"] = UP
                    elif event.key in (K_DOWN, K_s) and d != UP:
                        state["next_dir"] = DOWN
                    elif event.key in (K_LEFT, K_a) and d != RIGHT:
                        state["next_dir"] = LEFT
                    elif event.key in (K_RIGHT,K_d) and d != LEFT:
                        state["next_dir"] = RIGHT

            result = step(state)
            score  = state["score"]

            # Draw
            screen.fill(BLACK)
            if state["grid"]:
                draw_grid(screen)
            draw_walls(screen, state["walls"])
            draw_obstacles(screen, state["obstacles"])
            draw_snake(screen, state["snake"], state["snake_color"], state["snake_color_dark"])
            draw_food(screen, state["food"])
            draw_poison(screen, state["poison"])
            draw_powerup(screen, state["powerup"])
            draw_hud(screen, state, personal_best)
            pygame.display.flip()
            clock.tick(state["fps"])

        if result == "dead":
            return score, level

        # Level done
        next_level = level + 1
        screen_level_clear(level, next_level, score)
        level = next_level


# ================================================================
#  Entry point
# ================================================================

def main():
    sett = settings_mod.load()

    while True:
        action, username = screen_main_menu(sett, [None])

        if action == "quit":
            pygame.quit(); sys.exit()

        if action == "leaderboard":
            screen_leaderboard()
            continue

        if action == "settings":
            sett = screen_settings(sett)
            continue

        if action == "play":
            while True:
                final_score, final_level = play_game(username, sett)

                # Save to DB
                if DB_OK:
                    db.save_result(username, final_score, final_level)

                personal_best = db.get_personal_best(username)
                choice = screen_game_over(final_score, final_level, personal_best)

                if choice == "retry":
                    continue          # play again same username
                else:
                    break             # back to main menu


if __name__ == "__main__":
    main()