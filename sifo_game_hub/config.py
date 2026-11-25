"""Application paths and defaults."""
from pathlib import Path
import os

APP_NAME = "SIFO GAME HUB"
APP_VERSION = "1.0.0"
APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / "SIFOGameHub"
DB_PATH = APP_DIR / "sifo_game_hub.db"
LOG_PATH = APP_DIR / "sifo_game_hub.log"
DEFAULT_SETTINGS = {"theme": "dark", "accent": "#9B5CFF", "refresh_seconds": "3"}
