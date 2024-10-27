# config.py

import toml
import sys

CONFIG_FILE = "config.toml"

def load_config():
    try:
        config = toml.load(CONFIG_FILE)
    except FileNotFoundError:
        print(f"Configuration file {CONFIG_FILE} not found.")
        sys.exit(1)
    return config

config = load_config()

# Access settings with defaults
DB_PATH = config.get("database", {}).get("path", "task_manager.db")
DEFAULT_DURATION = config.get("settings", {}).get("default_duration", 25)
UPDATE_INTERVAL = config.get("timer", {}).get("update_interval", 1)
AUTO_START_BREAKS = config.get("timer", {}).get("auto_start_breaks", False)
CLEAR_SCREEN = config.get("display", {}).get("clear_screen", True)
THEME = config.get("display", {}).get("theme", "default")
LOG_LEVEL = config.get("logging", {}).get("level", "INFO")
LOG_FILE = config.get("logging", {}).get("log_file", None)
NOTIFICATIONS_ENABLED = config.get("notifications", {}).get("enable", True)
SOUND_ENABLED = config.get("notifications", {}).get("sound", True)
POPUP_DURATION = config.get("notifications", {}).get("popup_duration", 10)
