# ================================================================
#  game.py — Core game logic: snake, food, power-ups, obstacles
# ================================================================
import random
import pygame
from config import *


# ── Food helpers ────────────────────────────────────────────────

def pick_food_type():
    weights = [ft["weight"] for ft in FOOD_TYPES]
    total   = sum(weights)
    r       = random.uniform(0, total)
    cumul   = 0
    for ft in FOOD_TYPES:
        cumul += ft["weight"]
        if r <= cumul:
            return ft
    return FOOD_TYPES[0]


def food_time_left_ms(food, now_ms):
    if food is None:
        return 0
    elapsed = now_ms - food["spawned_ms"]
    return max(0, int(food["ftype"]["lifetime"] * 1000) - elapsed)


def spawn_food(snake_cells, walls, obstacles, poison_pos=None, powerup_pos=None):
    occupied = set(snake_cells) | walls | obstacles
    if poison_pos:
        occupied.add(poison_pos)
    if powerup_pos:
        occupied.add(powerup_pos)
    valid = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in occupied
    ]
    if not valid:
        return None
    pos   = random.choice(valid)
    ftype = pick_food_type()
    return {"pos": pos, "ftype": ftype, "spawned_ms": pygame.time.get_ticks()}


def spawn_poison(snake_cells, walls, obstacles, food_pos=None, powerup_pos=None):
    occupied = set(snake_cells) | walls | obstacles
    if food_pos:
        occupied.add(food_pos)
    if powerup_pos:
        occupied.add(powerup_pos)
    valid = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in occupied
    ]
    if not valid:
        return None
    pos = random.choice(valid)
    return {"pos": pos, "spawned_ms": pygame.time.get_ticks()}


# ── Power-up helpers ────────────────────────────────────────────

def spawn_powerup(snake_cells, walls, obstacles, food_pos=None, poison_pos=None):
    occupied = set(snake_cells) | walls | obstacles
    if food_pos:
        occupied.add(food_pos)
    if poison_pos:
        occupied.add(poison_pos)
    valid = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in occupied
    ]
    if not valid:
        return None
    pos  = random.choice(valid)
    ptype = random.choice(POWERUP_TYPES)
    return {"pos": pos, "ptype": ptype, "spawned_ms": pygame.time.get_ticks()}


# ── Obstacle helpers ────────────────────────────────────────────

def generate_obstacles(level, walls, snake_cells):
    """Place random obstacle blocks starting from level 3."""
    if level < OBSTACLES_FROM_LEVEL:
        return set()

    count    = min(6 + (level - OBSTACLES_FROM_LEVEL) * 2, 20)
    occupied = walls | set(snake_cells)
    # Safety buffer: no obstacles within 4 cells of snake head
    head     = snake_cells[0]
    buffer   = {
        (head[0] + dx, head[1] + dy)
        for dx in range(-4, 5)
        for dy in range(-4, 5)
    }
    candidates = [
        (c, r)
        for c in range(1, COLS - 1)
        for r in range(1, ROWS - 1)
        if (c, r) not in occupied and (c, r) not in buffer
    ]
    if not candidates:
        return set()

    chosen = set(random.sample(candidates, min(count, len(candidates))))

    # Simple connectivity check: verify snake head can still reach the center
    # (flood-fill from head, excluding walls+obstacles, must reach center)
    reachable = _flood(head, walls | chosen)
    center    = (COLS // 2, ROWS // 2)
    if center not in reachable or len(reachable) < 10:
        # Too isolated — give up and return fewer obstacles
        return set(random.sample(candidates, min(count // 2, len(candidates))))

    return chosen


def _flood(start, blocked):
    visited = set()
    stack   = [start]
    while stack:
        pos = stack.pop()
        if pos in visited or pos in blocked:
            continue
        c, r = pos
        if not (0 <= c < COLS and 0 <= r < ROWS):
            continue
        visited.add(pos)
        for dc, dr in [UP, DOWN, LEFT, RIGHT]:
            stack.append((c + dc, r + dr))
    return visited


# ── Border walls ────────────────────────────────────────────────

def border_walls():
    walls = set()
    for c in range(COLS):
        walls.add((c, 0))
        walls.add((c, ROWS - 1))
    for r in range(1, ROWS - 1):
        walls.add((0, r))
        walls.add((COLS - 1, r))
    return walls


def safe_start(walls):
    for dc in range(COLS // 2):
        col = COLS // 2 + dc
        row = ROWS // 2
        candidates = [(col - i, row) for i in range(3)]
        if all(c not in walls for c in candidates):
            return candidates
    return [(3, 1), (2, 1), (1, 1)]


# ── Game state factory ───────────────────────────────────────────

def new_game_state(level: int, score: int, settings: dict) -> dict:
    walls     = border_walls()
    snake     = safe_start(walls)
    obstacles = generate_obstacles(level, walls, snake)
    fps       = BASE_FPS + (level - 1) * FPS_INCREMENT

    snake_color      = tuple(settings.get("snake_color", [0, 200, 0]))
    snake_color_dark = tuple(max(0, c - 60) for c in snake_color)

    now = pygame.time.get_ticks()

    food    = spawn_food(snake, walls, obstacles)
    poison  = spawn_poison(snake, walls, obstacles, food_pos=food["pos"] if food else None)
    powerup = None  # spawned periodically during gameplay

    return {
        "snake":       snake,
        "direction":   RIGHT,
        "next_dir":    RIGHT,
        "walls":       walls,
        "obstacles":   obstacles,
        "food":        food,
        "poison":      poison,
        "powerup":     powerup,
        "score":       score,
        "level":       level,
        "fps":         fps,
        "base_fps":    fps,
        "foods_eaten": 0,
        # power-up state (active effect)
        "active_powerup":     None,   # ptype dict or None
        "powerup_end_ms":     0,
        "shield_active":      False,
        # timers
        "last_powerup_spawn": now,
        "powerup_spawn_interval": 10000,  # ms between powerup spawns
        # display settings
        "snake_color":      snake_color,
        "snake_color_dark": snake_color_dark,
        "grid":             settings.get("grid", False),
    }


# ── Step logic (called once per frame) ──────────────────────────

def step(state: dict) -> str:
    """
    Advance game by one tick.
    Returns: "alive" | "dead" | "level_done"
    """
    now = pygame.time.get_ticks()

    # Expire food timer
    food = state["food"]
    if food and food_time_left_ms(food, now) <= 0:
        state["food"] = spawn_food(
            state["snake"], state["walls"], state["obstacles"],
            poison_pos=state["poison"]["pos"] if state["poison"] else None,
            powerup_pos=state["powerup"]["pos"] if state["powerup"] else None,
        )

    # Expire powerup on field
    pu = state["powerup"]
    if pu and (now - pu["spawned_ms"]) > POWERUP_FIELD_LIFETIME:
        state["powerup"] = None

    # Spawn powerup periodically
    if state["powerup"] is None and (now - state["last_powerup_spawn"]) > state["powerup_spawn_interval"]:
        food_pos   = state["food"]["pos"]   if state["food"]   else None
        poison_pos = state["poison"]["pos"] if state["poison"] else None
        state["powerup"] = spawn_powerup(
            state["snake"], state["walls"], state["obstacles"],
            food_pos=food_pos, poison_pos=poison_pos
        )
        state["last_powerup_spawn"] = now

    # Expire active power-up effect
    ap = state["active_powerup"]
    if ap and ap["name"] != "shield" and now >= state["powerup_end_ms"]:
        state["active_powerup"] = None
        state["fps"]            = state["base_fps"]

    # Move
    state["direction"] = state["next_dir"]
    dx, dy  = state["direction"]
    hc, hr  = state["snake"][0]
    new_head = (hc + dx, hr + dy)

    # Collision: wall
    if new_head in state["walls"]:
        if state["shield_active"]:
            state["shield_active"]  = False
            state["active_powerup"] = None
            # Don't die — just don't move into the wall; stay
            return "alive"
        return "dead"

    # Collision: obstacle
    if new_head in state["obstacles"]:
        if state["shield_active"]:
            state["shield_active"]  = False
            state["active_powerup"] = None
            return "alive"
        return "dead"

    # Collision: self
    if new_head in state["snake"]:
        if state["shield_active"]:
            state["shield_active"]  = False
            state["active_powerup"] = None
            return "alive"
        return "dead"

    state["snake"].insert(0, new_head)

    # Eat food
    food = state["food"]
    if food and new_head == food["pos"]:
        state["score"]        += food["ftype"]["points"]
        state["foods_eaten"]  += 1
        state["food"]          = spawn_food(
            state["snake"], state["walls"], state["obstacles"],
            poison_pos=state["poison"]["pos"] if state["poison"] else None,
            powerup_pos=state["powerup"]["pos"] if state["powerup"] else None,
        )
        # Level done?
        if state["foods_eaten"] >= FOODS_PER_LEVEL:
            return "level_done"
        # Don't pop tail → snake grows
        return "alive"

    # Eat poison
    poison = state["poison"]
    if poison and new_head == poison["pos"]:
        # Shorten by 2
        for _ in range(2):
            if len(state["snake"]) > 1:
                state["snake"].pop()
        if len(state["snake"]) <= 1:
            return "dead"
        # Respawn poison
        food_pos = state["food"]["pos"] if state["food"] else None
        pu_pos   = state["powerup"]["pos"] if state["powerup"] else None
        state["poison"] = spawn_poison(
            state["snake"], state["walls"], state["obstacles"],
            food_pos=food_pos, powerup_pos=pu_pos
        )
        state["snake"].pop()  # remove tail (no growth)
        return "alive"

    # Collect power-up
    pu = state["powerup"]
    if pu and new_head == pu["pos"]:
        _apply_powerup(state, pu["ptype"], now)
        state["powerup"]           = None
        state["last_powerup_spawn"] = now  # reset spawn timer
        state["snake"].pop()
        return "alive"

    # Normal move — pop tail
    state["snake"].pop()
    return "alive"


def _apply_powerup(state, ptype, now):
    name = ptype["name"]
    state["active_powerup"] = ptype
    if name == "speed":
        state["fps"]           = state["base_fps"] + 4
        state["powerup_end_ms"] = now + ptype["duration"]
    elif name == "slow":
        state["fps"]           = max(2, state["base_fps"] - 3)
        state["powerup_end_ms"] = now + ptype["duration"]
    elif name == "shield":
        state["shield_active"] = True
        # shield lasts until triggered (no time limit)