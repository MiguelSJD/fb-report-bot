"""
Global worksheet schema and utility constants for F&B Bot.
"""

from typing import Final

from discord import app_commands

# Google Sheet Controls
TRIGGER_CELL: Final = "B2"
SHEET_UPDATE_DELAY: Final = 1.0
DATE_FORMAT: Final = "%d/%m/%Y"

# Discord API Controls
DISCORD_RATE_LIMIT_DELAY: Final = 0.5

# Activity Allowed Roles ID
ALLOWED_ROLE_IDS: Final[frozenset[int]] = frozenset(
    {
        1347188151214538853,
        1210459678895636491,
        1539015775526981662,
    }
)

# Cron Types
CRON_TYPE_CHOICES: Final[tuple[app_commands.Choice[str], ...]] = (
    app_commands.Choice[str](name="Daily Report", value="daily-report"),
    app_commands.Choice[str](name="Mid-Week Report", value="mid-week-report"),
    app_commands.Choice[str](name="Weekly Report", value="weekly-report"),
    app_commands.Choice[str](name="Quiz", value="quiz"),
)
