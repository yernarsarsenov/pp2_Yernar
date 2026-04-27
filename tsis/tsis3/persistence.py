"""persistence.py — Save/load leaderboard and settings to JSON files."""

import json
import os
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# ─── DEFAULT SETTINGS ────────────────────────────────────────────────────────

DEFAULT_SETTINGS = {
    "sound":       True,
    "car_color":   "blue",   # "blue" | "red" | "green" | "yellow"
    "difficulty":  "normal", # "easy" | "normal" | "hard"
}

# ─── SETTINGS ────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            # merge with defaults so missing keys are always present
            return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


# ─── LEADERBOARD ─────────────────────────────────────────────────────────────

def load_leaderboard() -> list:
    """Return list of dicts: [{name, score, distance, date}, ...]"""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_score(name: str, score: int, distance: int) -> None:
    """Append a new entry and keep top-10 sorted by score desc."""
    board = load_leaderboard()
    board.append({
        "name":     name,
        "score":    score,
        "distance": distance,
        "date":     datetime.now().strftime("%Y-%m-%d"),
    })
    board.sort(key=lambda e: e["score"], reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f, indent=2)