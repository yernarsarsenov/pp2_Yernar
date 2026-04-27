# ================================================================
#  settings.py — Load/save user preferences from settings.json
# ================================================================
import json
import os

SETTINGS_FILE = "settings.json"

DEFAULTS = {
    "snake_color": [0, 200, 0],   # RGB
    "grid":        False,
    "sound":       False,
}


def load() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            # Fill in any missing keys with defaults
            for k, v in DEFAULTS.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception as e:
            print(f"[Settings] Load failed: {e}")
    return dict(DEFAULTS)


def save(settings: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"[Settings] Save failed: {e}")