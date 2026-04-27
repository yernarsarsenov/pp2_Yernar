"""racer.py — Core gameplay: sprites, game loop, power-ups, obstacles."""
 
import pygame
import sys
import random
import time
from pygame.locals import *
 
# ─── PALETTE ─────────────────────────────────────────────────────────────────
 
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GREY  = (30,  30,  30)
MID_GREY   = (60,  60,  60)
LIGHT_GREY = (180, 180, 180)
ROAD_GREY  = (80,  80,  80)
YELLOW     = (255, 220,   0)
RED        = (220,  50,  50)
GREEN      = (50,  200,  80)
BLUE       = (50,  120, 220)
ORANGE     = (255, 140,   0)
CYAN       = (0,   210, 210)
PURPLE     = (160,  60, 220)
BROWN      = (120,  70,  20)
 
ACCENT     = (255, 200,   0)
 
CAR_COLORS = {
    "blue":   (50,  120, 220),
    "red":    (220,  50,  50),
    "green":  (50,  200,  80),
    "yellow": (255, 220,   0),
}
 
# ─── SCREEN / GAME CONSTANTS ─────────────────────────────────────────────────
 
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
FPS = 60
 
ROAD_LEFT  = SCREEN_WIDTH // 2 - 130
ROAD_RIGHT = SCREEN_WIDTH // 2 + 130
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
 
# Lanes
LANES = [
    ROAD_LEFT  + ROAD_WIDTH * 1 // 6,   # far-left
    ROAD_LEFT  + ROAD_WIDTH * 2 // 6,
    ROAD_LEFT  + ROAD_WIDTH * 3 // 6,   # center
    ROAD_LEFT  + ROAD_WIDTH * 4 // 6,
    ROAD_LEFT  + ROAD_WIDTH * 5 // 6,   # far-right
]
 
BASE_ENEMY_SPEED = 5
COINS_FOR_SPEED  = 10
 
 
# ─── SPRITE HELPERS ──────────────────────────────────────────────────────────
 
def make_car(color, w=40, h=60, is_enemy=False):
    """Draw a stylised top-down car on a transparent surface."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
 
    # Body
    body = pygame.Rect(4, 8, w - 8, h - 16)
    pygame.draw.rect(surf, color, body, border_radius=6)
 
    # Roof
    roof_color = tuple(max(0, c - 50) for c in color)
    pygame.draw.rect(surf, roof_color, (8, 18, w - 16, h - 36), border_radius=4)
 
    # Windscreens
    glass = (160, 210, 255, 200)
    if not is_enemy:
        pygame.draw.rect(surf, glass, (9, 22, w - 18, 14), border_radius=2)  # front
        pygame.draw.rect(surf, glass, (9, h - 36, w - 18, 10), border_radius=2)  # rear
    else:
        pygame.draw.rect(surf, glass, (9, h - 40, w - 18, 14), border_radius=2)  # front (facing down)
        pygame.draw.rect(surf, glass, (9, 26, w - 18, 10), border_radius=2)
 
    # Wheels
    wc = (20, 20, 20)
    for wx, wy in [(0, 10), (w - 8, 10), (0, h - 18), (w - 8, h - 18)]:
        pygame.draw.rect(surf, wc, (wx, wy, 8, 14), border_radius=3)
 
    # Enemy indicator light
    if is_enemy:
        pygame.draw.circle(surf, RED, (w // 2, h - 6), 4)
 
    return surf
 
 
def make_coin(value: int, radius: int = 11):
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
 
    if value == 1:
        col = YELLOW
    elif value == 2:
        col = ORANGE
    else:
        col = (255, 215, 0)
 
    pygame.draw.circle(surf, col,   (radius, radius), radius)
    pygame.draw.circle(surf, WHITE, (radius, radius), radius, 2)
 
    fnt   = pygame.font.SysFont("Verdana", 10, bold=True)
    label = fnt.render(str(value), True, BLACK)
    surf.blit(label, (radius - label.get_width() // 2,
                      radius - label.get_height() // 2))
    return surf
 
 
def make_obstacle(kind: str):
    """kind: 'oil' | 'pothole' | 'barrier' | 'bump'"""
    if kind == "oil":
        surf = pygame.Surface((44, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (20, 20, 80, 200), surf.get_rect())
        pygame.draw.ellipse(surf, (60, 60, 180, 120), surf.get_rect().inflate(-8, -6))
    elif kind == "pothole":
        surf = pygame.Surface((36, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (25, 20, 10, 220), surf.get_rect())
        pygame.draw.ellipse(surf, (15, 12, 5, 180), surf.get_rect().inflate(-6, -4))
    elif kind == "barrier":
        surf = pygame.Surface((20, 50), pygame.SRCALPHA)
        pygame.draw.rect(surf, ORANGE, (0, 0, 20, 50), border_radius=3)
        for i in range(0, 50, 10):
            c = BLACK if (i // 10) % 2 == 0 else ORANGE
            pygame.draw.rect(surf, c, (0, i, 20, 10))
    else:  # bump
        surf = pygame.Surface((50, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, MID_GREY, surf.get_rect())
        pygame.draw.ellipse(surf, YELLOW,   (0, 0, 50, 14), 2)
    return surf
 
 
def make_powerup(kind: str):
    """kind: 'nitro' | 'shield' | 'repair'"""
    surf = pygame.Surface((34, 34), pygame.SRCALPHA)
    if kind == "nitro":
        pygame.draw.polygon(surf, ORANGE,
                            [(17, 0), (28, 14), (22, 14), (28, 34), (10, 18), (17, 18), (10, 0)])
    elif kind == "shield":
        pygame.draw.polygon(surf, CYAN,
                            [(17, 2), (30, 10), (30, 22), (17, 32), (4, 22), (4, 10)])
        pygame.draw.polygon(surf, (*CYAN, 100),
                            [(17, 7), (25, 13), (25, 21), (17, 27), (9, 21), (9, 13)])
    else:  # repair
        pygame.draw.rect(surf, GREEN, (13, 4,  8, 26), border_radius=3)
        pygame.draw.rect(surf, GREEN, (4,  13, 26, 8),  border_radius=3)
        pygame.draw.rect(surf, WHITE, (15, 6,  4, 22), border_radius=2)
        pygame.draw.rect(surf, WHITE, (6,  15, 22, 4),  border_radius=2)
    return surf
 
 
# ─── SPRITES ─────────────────────────────────────────────────────────────────
 
class Player(pygame.sprite.Sprite):
    SPEED = 5
 
    def __init__(self, car_color="blue"):
        super().__init__()
        color      = CAR_COLORS.get(car_color, BLUE)
        self.image = make_car(color, 40, 60)
        self.rect  = self.image.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.shield_active = False
 
    def move(self):
        pressed = pygame.key.get_pressed()
        if pressed[K_LEFT]  and self.rect.left  > ROAD_LEFT  + 4:
            self.rect.x -= self.SPEED
        if pressed[K_RIGHT] and self.rect.right < ROAD_RIGHT - 4:
            self.rect.x += self.SPEED
 
 
class EnemyCar(pygame.sprite.Sprite):
    COLORS = [RED, (180, 60, 180), (60, 180, 180), (200, 120, 40)]
 
    def __init__(self, speed: float):
        super().__init__()
        color      = random.choice(self.COLORS)
        self.image = make_car(color, 40, 58, is_enemy=True)
        self.rect  = self.image.get_rect()
        self.speed = speed
        self._respawn()
 
    def _respawn(self):
        self.rect.centerx = random.choice(LANES)
        self.rect.bottom  = random.randint(-200, -40)
 
    def update(self, speed_override=None):
        s = speed_override if speed_override is not None else self.speed
        self.rect.y += s
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn()
 
 
class Coin(pygame.sprite.Sprite):
    WEIGHTS = [1, 2, 5]
 
    def __init__(self, fall_speed=3):
        super().__init__()
        self.weight  = random.choice(self.WEIGHTS)
        self.image   = make_coin(self.weight)
        self.rect    = self.image.get_rect()
        self.speed   = fall_speed
        self._respawn()
 
    def _respawn(self):
        self.rect.centerx = random.randint(ROAD_LEFT + 15, ROAD_RIGHT - 15)
        self.rect.bottom  = random.randint(-300, -20)
 
    def update(self, speed_override=None):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn()
 
 
class Obstacle(pygame.sprite.Sprite):
    KINDS = ["oil", "pothole", "barrier", "bump"]
 
    def __init__(self, kind: str = None, speed: float = 5):
        super().__init__()
        self.kind  = kind or random.choice(self.KINDS)
        self.image = make_obstacle(self.kind)
        self.rect  = self.image.get_rect()
        self.speed = speed
        self.rect.centerx = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20)
        self.rect.bottom  = random.randint(-400, -20)
        self.slowing = self.kind in ("oil", "bump")
 
    def update(self, speed_override=None):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
 
 
class PowerUp(pygame.sprite.Sprite):
    KINDS    = ["nitro", "shield", "repair"]
    LIFETIME = 7000   # ms before auto-disappear
 
    def __init__(self, speed: float = 4):
        super().__init__()
        self.kind       = random.choice(self.KINDS)
        self.image      = make_powerup(self.kind)
        self.rect       = self.image.get_rect()
        self.speed      = speed
        self.born_at    = pygame.time.get_ticks()
        self.rect.centerx = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20)
        self.rect.bottom  = random.randint(-300, -20)
 
    def update(self, *_):
        self.rect.y += self.speed
        alive = (pygame.time.get_ticks() - self.born_at < self.LIFETIME and
                 self.rect.top < SCREEN_HEIGHT)
        if not alive:
            self.kill()
 
 
# ─── SCROLLING ROAD BACKGROUND ────────────────────────────────────────────────
 
class Road:
    """Scrolling road with lane markings and side details."""
 
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.scroll = 0
 
    def update(self, speed):
        self.scroll = (self.scroll + speed) % 60
 
    def draw(self, surf):
        surf.fill(DARK_GREY)
 
        # Tarmac
        pygame.draw.rect(surf, ROAD_GREY,
                         (ROAD_LEFT, 0, ROAD_WIDTH, self.h))
 
        # Lane dashes
        dash_h, gap = 30, 20
        cycle = dash_h + gap
        for lane_x in LANES[1:-1]:
            for y in range(-cycle + int(self.scroll % cycle), self.h + cycle, cycle):
                pygame.draw.rect(surf, YELLOW, (lane_x - 2, y, 4, dash_h))
 
        # Road edges
        pygame.draw.line(surf, WHITE, (ROAD_LEFT, 0),  (ROAD_LEFT, self.h),  3)
        pygame.draw.line(surf, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, self.h), 3)
 
        # Grass texture lines
        for x in range(0, ROAD_LEFT - 10, 20):
            pygame.draw.line(surf, (55, 90, 40), (x, 0), (x, self.h), 1)
        for x in range(ROAD_RIGHT + 10, self.w, 20):
            pygame.draw.line(surf, (55, 90, 40), (x, 0), (x, self.h), 1)
 
 
# ─── HUD ─────────────────────────────────────────────────────────────────────
 
class HUD:
    def __init__(self, w, h):
        self.w, self.h  = w, h
        self.small      = pygame.font.SysFont("Verdana", 16, bold=True)
        self.tiny       = pygame.font.SysFont("Verdana", 12)
 
    def draw(self, surf, score, coins, distance, speed, active_pu, pu_remaining_ms,
             has_shield, dist_to_finish):
        # Top bar background
        bar = pygame.Surface((self.w, 36), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 170))
        surf.blit(bar, (0, 0))
 
        # Score / Coins / Distance
        self._blit(surf, f"⭐ {score}",     WHITE,  10,  9)
        self._blit(surf, f"🪙 {coins}",     YELLOW, self.w // 2 - 30, 9)
        self._blit(surf, f"📏 {distance}m", CYAN,   self.w - 100, 9)
 
        # Bottom bar for power-up status
        if active_pu:
            bar2 = pygame.Surface((self.w, 28), pygame.SRCALPHA)
            bar2.fill((0, 0, 0, 150))
            surf.blit(bar2, (0, self.h - 28))
 
            icons = {"nitro": "⚡", "shield": "🛡", "repair": "➕"}
            secs  = max(0, pu_remaining_ms // 1000)
            colors = {"nitro": ORANGE, "shield": CYAN, "repair": GREEN}
            label = f"{icons.get(active_pu, '?')} {active_pu.upper()}"
            if active_pu != "repair":
                label += f"  {secs}s"
            if active_pu == "shield":
                label += "  [until hit]"
            self._blit(surf, label, colors.get(active_pu, WHITE), 10, self.h - 22)
 
        # Shield ring around car
        if has_shield:
            pass  # drawn separately in run()
 
    def _blit(self, surf, text, color, x, y):
        s = self.small.render(text, True, color)
        surf.blit(s, (x, y))
 
 
# ─── DIFFICULTY CONFIG ────────────────────────────────────────────────────────
 
DIFF_CONFIG = {
    "easy":   dict(base_speed=4,  max_enemies=2, obstacle_interval=5000, pu_interval=3500),
    "normal": dict(base_speed=5,  max_enemies=3, obstacle_interval=3500, pu_interval=5000),
    "hard":   dict(base_speed=7,  max_enemies=5, obstacle_interval=2000, pu_interval=7000),
}
 
# ─── MAIN GAME FUNCTION ───────────────────────────────────────────────────────
 
def run_game(surf: pygame.Surface, clock: pygame.time.Clock,
             player_name: str, settings: dict) -> tuple:
    """
    Run one round of the game.
    Returns (score, distance, coins).
    """
 
    diff   = settings.get("difficulty", "normal")
    cfg    = DIFF_CONFIG.get(diff, DIFF_CONFIG["normal"])
    sound  = settings.get("sound", True)
 
    BASE_SPEED   = cfg["base_speed"]
    MAX_ENEMIES  = cfg["max_enemies"]
 
    road   = Road(SCREEN_WIDTH, SCREEN_HEIGHT)
    hud    = HUD(SCREEN_WIDTH, SCREEN_HEIGHT)
    player = Player(settings.get("car_color", "blue"))
 
    # Sprite groups
    all_sprites    = pygame.sprite.Group()
    enemy_group    = pygame.sprite.Group()
    coin_group     = pygame.sprite.Group()
    obstacle_group = pygame.sprite.Group()
    powerup_group  = pygame.sprite.Group()
 
    all_sprites.add(player)
 
    # Initial enemies
    for _ in range(MAX_ENEMIES):
        e = EnemyCar(BASE_SPEED)
        enemy_group.add(e)
        all_sprites.add(e)
 
    # Initial coins
    for _ in range(3):
        c = Coin()
        coin_group.add(c)
        all_sprites.add(c)
 
    # Game state
    score    = 0
    coins    = 0
    distance = 0
    speed    = BASE_SPEED
    frame    = 0
 
    # Power-up state
    active_pu      = None
    pu_end_time    = 0
    pu_durations   = {"nitro": 4000, "shield": 0, "repair": 0}
 
    # Slowdown overlay state (oil / bump)
    slow_until = 0
 
    # Timers
    SPAWN_COIN     = pygame.USEREVENT + 1
    SPAWN_OBSTACLE = pygame.USEREVENT + 2
    SPAWN_POWERUP  = pygame.USEREVENT + 3
    SPAWN_ENEMY    = pygame.USEREVENT + 4
    TICK_SCORE     = pygame.USEREVENT + 5
 
    pygame.time.set_timer(SPAWN_COIN,     4000)
    pygame.time.set_timer(SPAWN_OBSTACLE, cfg["obstacle_interval"])
    pygame.time.set_timer(SPAWN_POWERUP,  cfg["pu_interval"])
    pygame.time.set_timer(SPAWN_ENEMY,    8000)
    pygame.time.set_timer(TICK_SCORE,     1000)
 
    running = True
    while running:
 
        dt = clock.tick(FPS)
        frame += 1
 
        # ─── EVENTS ──────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
 
            elif event.type == SPAWN_COIN:
                if random.random() < 0.7:
                    nc = Coin(fall_speed=max(2, speed // 2))
                    coin_group.add(nc); all_sprites.add(nc)
 
            elif event.type == SPAWN_OBSTACLE:
                # Safe spawn: not too close to player
                obs = Obstacle(speed=speed * 0.9)
                # Retry if spawning on player
                for _ in range(5):
                    if abs(obs.rect.centerx - player.rect.centerx) > 30:
                        break
                    obs.rect.centerx = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20)
                obstacle_group.add(obs); all_sprites.add(obs)
 
            elif event.type == SPAWN_POWERUP:
                if not any(p for p in powerup_group):  # max 1 on screen
                    pu = PowerUp(speed=max(2, speed // 2))
                    powerup_group.add(pu); all_sprites.add(pu)
 
            elif event.type == SPAWN_ENEMY:
                current_enemies = len(enemy_group)
                cap = MAX_ENEMIES + coins // 20  # scale with score
                if current_enemies < cap:
                    ne = EnemyCar(speed)
                    enemy_group.add(ne); all_sprites.add(ne)
 
            elif event.type == TICK_SCORE:
                score    += 1
                distance += int(speed * 2)
 
        # ─── SPEED CALCULATION ───────────────────────────────────────────
        now = pygame.time.get_ticks()
 
        base_speed = BASE_SPEED + (coins // COINS_FOR_SPEED)
 
        if active_pu == "nitro" and now < pu_end_time:
            speed = base_speed * 2
        elif now < slow_until:
            speed = max(1, base_speed // 2)
        else:
            speed = base_speed
 
        # ─── MOVE ────────────────────────────────────────────────────────
        player.move()
        road.update(speed)
 
        for e in enemy_group:
            e.update(speed)
        for c in coin_group:
            c.update(max(2, speed // 2))
        for obs in obstacle_group:
            obs.update(speed * 0.9)
        powerup_group.update()
 
        # ─── COIN COLLISION ──────────────────────────────────────────────
        collected = pygame.sprite.spritecollide(player, coin_group, True)
        for coin in collected:
            coins += coin.weight
            # Respawn
            nc = Coin(fall_speed=max(2, speed // 2))
            coin_group.add(nc); all_sprites.add(nc)
 
        # ─── POWER-UP COLLECTION ─────────────────────────────────────────
        pu_hit = pygame.sprite.spritecollide(player, powerup_group, True)
        for pu in pu_hit:
            if active_pu is None:  # only one at a time
                active_pu = pu.kind
                if pu.kind == "nitro":
                    pu_end_time = now + pu_durations["nitro"]
                elif pu.kind == "repair":
                    # Instant: clear one obstacle near player
                    nearest = None
                    for obs in obstacle_group:
                        if nearest is None or (
                            abs(obs.rect.centery - player.rect.centery) <
                            abs(nearest.rect.centery - player.rect.centery)
                        ):
                            nearest = obs
                    if nearest:
                        nearest.kill()
                    # auto-clear power-up state
                    pu_end_time = now + 500  # brief flash
                # shield: stays until hit (no timer)
 
        # Expire power-up (nitro / repair)
        if active_pu in ("nitro", "repair") and now > pu_end_time:
            active_pu = None
 
        # ─── OBSTACLE COLLISION ──────────────────────────────────────────
        obs_hit = pygame.sprite.spritecollide(player, obstacle_group, True)
        for obs in obs_hit:
            if active_pu == "shield":
                active_pu = None   # shield absorbs one hit
            elif obs.slowing:
                slow_until = now + 2000  # slow for 2 sec
            else:
                # barrier / pothole → game over
                running = False
                break
 
        # ─── ENEMY COLLISION ─────────────────────────────────────────────
        if pygame.sprite.spritecollideany(player, enemy_group):
            if active_pu == "shield":
                active_pu = None
                # Push enemies away briefly
                for e in enemy_group:
                    if e.rect.colliderect(player.rect):
                        e.rect.y -= 80
            else:
                running = False
 
        # ─── DRAW ────────────────────────────────────────────────────────
        road.draw(surf)
 
        # Draw sprites manually (control draw order)
        for obs in obstacle_group:
            surf.blit(obs.image, obs.rect)
        for c in coin_group:
            surf.blit(c.image, c.rect)
        for pu in powerup_group:
            # Pulsing outline
            pulse = abs(pygame.math.Vector2(0, 1).rotate(now * 0.2).y)
            r_exp = int(pulse * 6)
            pygame.draw.circle(surf, (*ACCENT, 80),
                                pu.rect.center, pu.rect.width // 2 + 6 + r_exp, 2)
            surf.blit(pu.image, pu.rect)
        for e in enemy_group:
            surf.blit(e.image, e.rect)
 
        # Shield glow around player
        if active_pu == "shield":
            glow_r = max(player.rect.width, player.rect.height) // 2 + 6
            pygame.draw.circle(surf, CYAN, player.rect.center, glow_r + 4, 3)
            pygame.draw.circle(surf, (*CYAN, 60), player.rect.center, glow_r + 8, 1)
 
        surf.blit(player.image, player.rect)
 
        # HUD
        pu_rem = max(0, pu_end_time - now) if active_pu in ("nitro",) else 0
        hud.draw(surf, score, coins, distance, speed, active_pu, pu_rem,
                 active_pu == "shield", 0)
 
        # Speed indicator
        spd_surf = pygame.font.SysFont("Verdana", 11).render(
            f"SPD {speed}", True, LIGHT_GREY)
        surf.blit(spd_surf, (SCREEN_WIDTH - spd_surf.get_width() - 8, 40))
 
        # Nitro overlay flash
        if active_pu == "nitro":
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(40 + 20 * abs(pygame.math.Vector2(1, 0).rotate(now * 0.5).x))
            flash.fill((255, 200, 0, alpha))
            surf.blit(flash, (0, 0))
 
        pygame.display.flip()
 
    # ─── GAME OVER FLASH ─────────────────────────────────────────────────
    _crash_flash(surf, clock, score, coins, distance, sound)
 
    # Cancel timers
    for ev in (SPAWN_COIN, SPAWN_OBSTACLE, SPAWN_POWERUP, SPAWN_ENEMY, TICK_SCORE):
        pygame.time.set_timer(ev, 0)
 
    return score, distance, coins
 
 
def _crash_flash(surf, clock, score, coins, distance, sound):
    """Brief red-flash crash animation."""
    try:
        pygame.mixer.Sound("racer_crash.wav").play()
    except Exception:
        pass
 
    fnt = pygame.font.SysFont("Verdana", 48, bold=True)
    for i in range(20):
        clock.tick(30)
        alpha = max(0, 255 - i * 10)
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((220, 30, 30, alpha))
        surf.blit(overlay, (0, 0))
        t = fnt.render("CRASH!", True, WHITE)
        surf.blit(t, (surf.get_width() // 2 - t.get_width() // 2,
                      surf.get_height() // 2 - 30))
        pygame.display.flip()