"""
Global worksheet schema and utility constants for FB Report Bot.
"""

# Google Sheet Controls
TRIGGER_CELL = "B2"
SHEET_UPDATE_DELAY = 1.0
DATE_FORMAT = "%d/%m/%Y"

# Column Mapping (0-indexed)
COL_DATE = 0
COL_TOPIC = 2
COL_OBSERVATION = 3
COL_CONSEQUENCE = 4
COL_SOLUTION = 5
COL_VOTES = 6

# Discord API Controls
DISCORD_RATE_LIMIT_DELAY = 0.5
