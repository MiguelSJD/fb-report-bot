"""
Global worksheet schema and utility constants for F&B Bot.
"""

from typing import Final

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
