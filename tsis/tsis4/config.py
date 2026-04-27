# ================================================================
#  config.py — Central configuration
# ================================================================

CELL       = 20
COLS       = 30
ROWS       = 28
HUD_HEIGHT = 60

SCREEN_W = COLS * CELL
SCREEN_H = ROWS * CELL + HUD_HEIGHT

# Colours
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
GREEN       = (0,   200, 0)
DARK_GREEN  = (0,   140, 0)
RED         = (220, 0,   0)
DARK_RED    = (120, 0,   0)
GRAY        = (50,  50,  50)
LIGHT_GRAY  = (160, 160, 160)
DARK_GRAY   = (80,  80,  80)
GOLD        = (255, 215, 0)
SILVER      = (192, 192, 192)
ORANGE      = (255, 140, 0)
CYAN        = (0,   220, 220)
PURPLE      = (180, 0,   220)
BLUE        = (30,  100, 255)
YELLOW      = (255, 240, 0)

UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

FOODS_PER_LEVEL  = 5
BASE_FPS         = 8
FPS_INCREMENT    = 2

FOOD_TYPES = [
    {"name": "normal", "color": RED,    "points": 5,  "lifetime": 8.0, "weight": 60},
    {"name": "silver", "color": SILVER, "points": 15, "lifetime": 5.0, "weight": 30},
    {"name": "gold",   "color": GOLD,   "points": 30, "lifetime": 3.0, "weight": 10},
]

POWERUP_TYPES = [
    {"name": "speed",  "color": ORANGE, "label": "⚡SPEED",  "duration": 5000},
    {"name": "slow",   "color": CYAN,   "label": "🐢SLOW",   "duration": 5000},
    {"name": "shield", "color": PURPLE, "label": "🛡SHIELD", "duration": 0},   # until triggered
]

POWERUP_FIELD_LIFETIME = 8000   # ms before disappearing from field
OBSTACLES_FROM_LEVEL   = 3
OBSTACLE_COLOR         = (100, 80, 60)