"""
Application runtime settings loaded from environment variables.
"""

import os
from pathlib import Path

# User Permissions
raw_user_ids = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS = [
    int(uid.strip()) for uid in raw_user_ids.split(",") if uid.strip().isdigit()
]

# Paths
DATA_ROOT = Path(os.getenv("DATA_ROOT", "/app/data"))
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_ROOT / "system" / "servers_settings.db")))

# Secrets & Service Keys
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPREADSHEET_URL = os.getenv("SPREADSHEET_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
