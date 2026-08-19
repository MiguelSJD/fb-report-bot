"""
Schema initialization orchestrator.
"""

import sqlite3

from config import DB_PATH
from models.log_level import LogLevel
from utils.database import get_db_connection
from utils.logger import log_event
from utils.quiz_db import init_quiz_table
from utils.settings_db import init_settings_table

SCHEMA_INITIALIZERS = [
    init_settings_table,
    init_quiz_table,
]


def initialize_database() -> None:
    """Execute all registered schema initializers within a single transaction."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for init_schema in SCHEMA_INITIALIZERS:
                init_schema(cursor)
            conn.commit()
            log_event(
                None, LogLevel.INFO, f"Database initialized successfully at: {DB_PATH}"
            )
    except (sqlite3.Error, OSError) as exc:
        log_event(
            None, LogLevel.CRITICAL, f"Failed to initialize database: {exc}", exc=exc
        )
