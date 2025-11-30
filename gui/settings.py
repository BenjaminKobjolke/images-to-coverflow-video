"""Settings persistence for the GUI application."""
import json
from pathlib import Path
from typing import Any, Dict

# Default settings
DEFAULTS = {
    "theme": "Dark",
    "sidebar_columns": 1,
    "last_project": None,
    "window_width": 1200,
    "window_height": 800,
    "window_x": None,  # None = center on screen
    "window_y": None,
    "window_maximized": False,
}


def get_settings_path() -> Path:
    """Return the path to the settings file."""
    return Path(__file__).parent / "config.json"


def load_settings() -> Dict[str, Any]:
    """Load settings from JSON config file.

    Returns default settings if file doesn't exist or is invalid.
    """
    path = get_settings_path()
    if not path.exists():
        return DEFAULTS.copy()

    try:
        with open(path, "r") as f:
            data = json.load(f)
        # Merge with defaults to ensure all keys exist
        settings = DEFAULTS.copy()
        settings.update(data)
        return settings
    except (json.JSONDecodeError, IOError):
        return DEFAULTS.copy()


def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to JSON config file."""
    path = get_settings_path()
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
