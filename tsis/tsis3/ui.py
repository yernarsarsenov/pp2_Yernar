"""ui.py — All non-gameplay Pygame screens."""

import pygame
import sys
from pygame.locals import *
from persistence import load_leaderboard, save_settings

# ─── PALETTE ─────────────────────────────────────────────────────────────────

BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GREY  = (30,  30,  30)
MID_GREY   = (60,  60,  60)
LIGHT_GREY = (180, 180, 180)
ROAD_GREY  = (80,  80,  80)
YELLOW     = (255, 220,  0)
RED        = (220,  50,  50)
GREEN      = (50,  200,  80)
BLUE       = (50,  120, 220)
ORANGE     = (255, 140,   0)
CYAN       = (0,   210, 210)

ACCENT     = (255, 200,  0)   # gold-yellow

CAR_COLORS = {
    "blue":   (50,  120, 220),
    "red":    (220,  50,  50),
    "green":  (50,  200,  80),
    "yellow": (255, 220,   0),
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _centered_rect(surf: pygame.Surface, w: int, h: int, cy: int) -> pygame.Rect:
    return pygame.Rect((surf.get_width() - w) // 2, cy - h // 2, w, h)


class Button:
    """Simple clickable rounded rectangle button."""
    PAD = 12

    def __init__(self, surf: pygame.Surface, text: str,
                 cy: int, w: int = 200, h: int = 46,
                 color=ACCENT, text_color=BLACK, font=None):
        self.surf  = surf
        self.rect  = _centered_rect(surf, w, h, cy)
        self.text  = text
        self.color = color
        self.text_color = text_color
        self.font  = font or pygame.font.SysFont("Verdana", 18, bold=True)
        self.hovered = False

    def draw(self):
        col = tuple(min(255, c + 40) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(self.surf, col, self.rect, border_radius=8)
        pygame.draw.rect(self.surf, WHITE, self.rect, 2, border_radius=8)
        label = self.font.render(self.text, True, self.text_color)
        lx = self.rect.centerx - label.get_width()  // 2
        ly = self.rect.centery - label.get_height() // 2
        self.surf.blit(label, (lx, ly))

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event) -> bool:
        return (event.type == MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ─── ROAD BACKGROUND HELPER ──────────────────────────────────────────────────

def _draw_road_bg(surf: pygame.Surface, scroll: int = 0):
    W, H = surf.get_size()
    surf.fill(DARK_GREY)

    # Tarmac
    road_rect = pygame.Rect(W // 2 - 130, 0, 260, H)
    pygame.draw.rect(surf, ROAD_GREY, road_rect)

    # Lane dashes
    dash_h, gap = 30, 20
    cycle = dash_h + gap
    for lane_x in (W // 2 - 43, W // 2 + 43):
        for y in range(-(scroll % cycle), H, cycle):
            pygame.draw.rect(surf, YELLOW, (lane_x - 2, y, 4, dash_h))

    # Road edges
    pygame.draw.line(surf, WHITE, (W // 2 - 130, 0), (W // 2 - 130, H), 3)
    pygame.draw.line(surf, WHITE, (W // 2 + 130, 0), (W // 2 + 130, H), 3)


# ─── SCREENS ─────────────────────────────────────────────────────────────────

def screen_username(surf: pygame.Surface, clock: pygame.time.Clock,
                    settings: dict) -> str:
    """Ask player for a username. Returns the entered name."""
    W, H = surf.get_size()
    title_font = pygame.font.SysFont("Verdana", 36, bold=True)
    label_font = pygame.font.SysFont("Verdana", 20)
    scroll = 0
    name   = ""
    cursor_visible = True
    cursor_timer   = 0

    done_btn = Button(surf, "START RACE ▶", H // 2 + 70, w=220, h=48)

    while True:
        dt = clock.tick(60)
        scroll = (scroll + 3) % 100
        cursor_timer += dt
        if cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer   = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode
            if done_btn.is_clicked(event) and name.strip():
                return name.strip()

        done_btn.update(pygame.mouse.get_pos())

        _draw_road_bg(surf, scroll)

        # Title
        title = title_font.render("RACER", True, ACCENT)
        surf.blit(title, (W // 2 - title.get_width() // 2, 80))

        sub = label_font.render("Enter your name to begin", True, LIGHT_GREY)
        surf.blit(sub, (W // 2 - sub.get_width() // 2, 145))

        # Input box
        box_rect = pygame.Rect(W // 2 - 130, H // 2 - 30, 260, 46)
        pygame.draw.rect(surf, MID_GREY, box_rect, border_radius=6)
        pygame.draw.rect(surf, ACCENT,   box_rect, 2, border_radius=6)

        disp = name + ("|" if cursor_visible else "")
        name_surf = label_font.render(disp, True, WHITE)
        surf.blit(name_surf, (box_rect.x + 10, box_rect.y + 12))

        done_btn.draw()
        pygame.display.flip()


def screen_main_menu(surf: pygame.Surface, clock: pygame.time.Clock,
                     settings: dict):
    """
    Returns one of: 'play', 'leaderboard', 'settings', 'quit'
    """
    W, H = surf.get_size()
    title_font = pygame.font.SysFont("Verdana", 46, bold=True)
    sub_font   = pygame.font.SysFont("Verdana", 14)
    scroll = 0

    btns = [
        Button(surf, "▶  PLAY",        H // 2 - 60, w=220, h=50),
        Button(surf, "🏆  LEADERBOARD", H // 2,      w=220, h=50),
        Button(surf, "⚙  SETTINGS",    H // 2 + 60,  w=220, h=50),
        Button(surf, "✕  QUIT",         H // 2 + 120, w=220, h=50,
               color=(160, 40, 40), text_color=WHITE),
    ]
    actions = ["play", "leaderboard", "settings", "quit"]

    while True:
        clock.tick(60)
        scroll = (scroll + 3) % 100

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            for btn, action in zip(btns, actions):
                if btn.is_clicked(event):
                    return action

        mouse = pygame.mouse.get_pos()
        _draw_road_bg(surf, scroll)

        # Panel
        panel = pygame.Surface((280, 340), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        surf.blit(panel, (W // 2 - 140, H // 2 - 100))

        title = title_font.render("RACER", True, ACCENT)
        surf.blit(title, (W // 2 - title.get_width() // 2, 90))

        tag = sub_font.render("TSIS 3 — Advanced Driving", True, LIGHT_GREY)
        surf.blit(tag, (W // 2 - tag.get_width() // 2, 148))

        for btn in btns:
            btn.update(mouse)
            btn.draw()

        pygame.display.flip()


def screen_settings(surf: pygame.Surface, clock: pygame.time.Clock,
                    settings: dict) -> dict:
    """
    Interactive settings screen. Returns updated settings dict.
    """
    W, H  = surf.get_size()
    title_font = pygame.font.SysFont("Verdana", 30, bold=True)
    label_font = pygame.font.SysFont("Verdana", 18)
    scroll = 0

    # Working copy
    s = settings.copy()
    difficulties = ["easy", "normal", "hard"]
    car_colors   = list(CAR_COLORS.keys())

    back_btn = Button(surf, "← BACK", H - 60, w=160, h=44)

    while True:
        clock.tick(60)
        scroll = (scroll + 2) % 100
        mouse  = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Sound toggle
                if sound_rect.collidepoint(event.pos):
                    s["sound"] = not s["sound"]
                # Car color cycle
                if color_rect.collidepoint(event.pos):
                    idx = car_colors.index(s["car_color"])
                    s["car_color"] = car_colors[(idx + 1) % len(car_colors)]
                # Difficulty cycle
                if diff_rect.collidepoint(event.pos):
                    idx = difficulties.index(s["difficulty"])
                    s["difficulty"] = difficulties[(idx + 1) % len(difficulties)]
                if back_btn.is_clicked(event):
                    save_settings(s)
                    return s

        back_btn.update(mouse)
        _draw_road_bg(surf, scroll)

        # Semi-transparent panel
        panel = pygame.Surface((300, 280), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        surf.blit(panel, (W // 2 - 150, 90))

        t = title_font.render("SETTINGS", True, ACCENT)
        surf.blit(t, (W // 2 - t.get_width() // 2, 100))

        y = 160

        def row(label_text: str, value_text: str, value_color=WHITE):
            nonlocal y
            lbl = label_font.render(label_text, True, LIGHT_GREY)
            val = label_font.render(value_text, True, value_color)
            surf.blit(lbl, (W // 2 - 130, y))
            surf.blit(val, (W // 2 + 30,  y))
            r = pygame.Rect(W // 2 + 25, y - 2, val.get_width() + 10, val.get_height() + 4)
            pygame.draw.rect(surf, ACCENT, r, 1, border_radius=4)
            y += 52
            return r

        sound_rect = row("Sound",      "ON" if s["sound"] else "OFF",
                         GREEN if s["sound"] else RED)
        color_rect  = row("Car Color",  s["car_color"].capitalize(),
                          CAR_COLORS[s["car_color"]])
        diff_rect   = row("Difficulty", s["difficulty"].capitalize())

        hint = pygame.font.SysFont("Verdana", 12).render(
            "Click values to cycle options", True, LIGHT_GREY)
        surf.blit(hint, (W // 2 - hint.get_width() // 2, 340))

        back_btn.draw()
        pygame.display.flip()


def screen_leaderboard(surf: pygame.Surface, clock: pygame.time.Clock):
    """Show top-10 leaderboard. Returns when Back is pressed."""
    W, H  = surf.get_size()
    title_font = pygame.font.SysFont("Verdana", 28, bold=True)
    hdr_font   = pygame.font.SysFont("Verdana", 14, bold=True)
    row_font   = pygame.font.SysFont("Verdana", 14)
    scroll = 0

    board     = load_leaderboard()
    back_btn  = Button(surf, "← BACK", H - 60, w=160, h=44)

    while True:
        clock.tick(60)
        scroll = (scroll + 2) % 100

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if back_btn.is_clicked(event):
                return

        back_btn.update(pygame.mouse.get_pos())
        _draw_road_bg(surf, scroll)

        panel = pygame.Surface((340, 420), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 190))
        surf.blit(panel, (W // 2 - 170, 60))

        t = title_font.render("🏆  TOP  10", True, ACCENT)
        surf.blit(t, (W // 2 - t.get_width() // 2, 72))

        # Header
        headers = ["#", "Name", "Score", "Dist", "Date"]
        xs      = [W // 2 - 155, W // 2 - 115, W // 2 + 20, W // 2 + 80, W // 2 + 130]
        for hdr, x in zip(headers, xs):
            h_surf = hdr_font.render(hdr, True, ACCENT)
            surf.blit(h_surf, (x, 112))

        pygame.draw.line(surf, ACCENT, (W // 2 - 160, 130), (W // 2 + 160, 130), 1)

        if not board:
            empty = row_font.render("No scores yet — race to set one!", True, LIGHT_GREY)
            surf.blit(empty, (W // 2 - empty.get_width() // 2, 200))
        else:
            for i, entry in enumerate(board[:10]):
                color = ACCENT if i == 0 else (LIGHT_GREY if i < 3 else WHITE)
                ry    = 140 + i * 28
                vals  = [
                    str(i + 1),
                    entry.get("name",     "?")[:8],
                    str(entry.get("score",    0)),
                    f'{entry.get("distance", 0)}m',
                    entry.get("date",     ""),
                ]
                for val, x in zip(vals, xs):
                    surf.blit(row_font.render(val, True, color), (x, ry))

        back_btn.draw()
        pygame.display.flip()


def screen_game_over(surf: pygame.Surface, clock: pygame.time.Clock,
                     score: int, distance: int, coins: int,
                     settings: dict):
    """
    Game-over screen. Returns 'retry' or 'menu'.
    """
    W, H  = surf.get_size()
    big_font   = pygame.font.SysFont("Verdana", 40, bold=True)
    label_font = pygame.font.SysFont("Verdana", 18)
    scroll = 0

    retry_btn = Button(surf, "🔄  RETRY",     H // 2 + 60,  w=200, h=48, color=GREEN,  text_color=BLACK)
    menu_btn  = Button(surf, "🏠  MAIN MENU", H // 2 + 120, w=200, h=48, color=MID_GREY)

    while True:
        clock.tick(60)
        scroll = (scroll + 2) % 100
        mouse  = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if retry_btn.is_clicked(event):
                return "retry"
            if menu_btn.is_clicked(event):
                return "menu"

        retry_btn.update(mouse)
        menu_btn.update(mouse)

        surf.fill((180, 30, 30))
        _draw_road_bg(surf, scroll)

        # Dark overlay
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((180, 0, 0, 120))
        surf.blit(overlay, (0, 0))

        go = big_font.render("GAME OVER", True, WHITE)
        surf.blit(go, (W // 2 - go.get_width() // 2, 110))

        stats = [
            ("Score",    str(score)),
            ("Distance", f"{distance} m"),
            ("Coins",    str(coins)),
        ]
        y = 200
        for lbl, val in stats:
            l_surf = label_font.render(f"{lbl}:", True, LIGHT_GREY)
            v_surf = label_font.render(val,       True, ACCENT)
            surf.blit(l_surf, (W // 2 - 90, y))
            surf.blit(v_surf, (W // 2 + 20, y))
            y += 34

        retry_btn.draw()
        menu_btn.draw()
        pygame.display.flip()