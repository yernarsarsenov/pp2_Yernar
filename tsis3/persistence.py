import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_leaderboard():
    return load_json(LEADERBOARD_FILE, [])

def save_score(name, score, distance):
    leaderboard = get_leaderboard()
    leaderboard.append({"name": name, "score": score, "distance": round(distance, 2)})
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]
    save_json(LEADERBOARD_FILE, leaderboard)

def get_settings():
    default = {
        "sound": True,
        "car_color": "Red",
        "difficulty": "Medium"
    }
    return load_json(SETTINGS_FILE, default)

def save_settings(settings):
    save_json(SETTINGS_FILE, settings)
