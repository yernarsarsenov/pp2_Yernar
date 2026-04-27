"""main.py — Entry point: wires together all screens and game loop."""

import pygame
import sys
from pygame.locals import *

from persistence import load_settings, save_settings, save_score
from ui          import (screen_username, screen_main_menu,
                          screen_settings, screen_leaderboard,
                          screen_game_over)
from racer       import run_game

# ─── INIT ────────────────────────────────────────────────────────────────────

pygame.init()

SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

surf  = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RACER — TSIS 3")
clock = pygame.time.Clock()

# ─── LOAD SETTINGS ───────────────────────────────────────────────────────────

settings = load_settings()

# ─── MAIN FLOW ───────────────────────────────────────────────────────────────

player_name = ""

while True:

    # ── Ask username if we don't have one yet ─────────────────────────────
    if not player_name:
        player_name = screen_username(surf, clock, settings)

    # ── Main menu ─────────────────────────────────────────────────────────
    action = screen_main_menu(surf, clock, settings)

    if action == "quit":
        pygame.quit()
        sys.exit()

    elif action == "leaderboard":
        screen_leaderboard(surf, clock)

    elif action == "settings":
        settings = screen_settings(surf, clock, settings)
        save_settings(settings)

    elif action == "play":
        # Game loop with retry support
        while True:
            score, distance, coins = run_game(surf, clock, player_name, settings)

            # Persist result
            save_score(player_name, score, distance)

            # Game-over screen
            choice = screen_game_over(surf, clock, score, distance, coins, settings)

            if choice == "retry":
                continue   # play again immediately
            else:
                break      # back to main menu