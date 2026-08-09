"""
Database connection and initialization helper for FB Report Bot.
Manages database connection lifecycle and schema initialization.
"""

import os
import sqlite3
from contextlib import contextmanager

from config import DB_PATH
from models.log_level import LogLevel
from utils.logger import log_event


def ensure_db_directory():
    """Ensure the directory for the database file exists."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


@contextmanager
def get_db_connection():
    """Context manager for SQLite database connections."""
    ensure_db_directory()
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        yield conn
    except (sqlite3.Error, OSError) as exc:
        log_event(
            None, LogLevel.ERROR, f"SQLite database connection error: {exc}", exc=exc
        )
        raise
    finally:
        if conn:
            conn.close()


def initialize_database():
    """Create the guild_channels table if it doesn't exist."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS guild_channels
                (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
            log_event(
                None, LogLevel.INFO, f"Database initialized successfully at: {DB_PATH}"
            )
    except (sqlite3.Error, OSError) as exc:
        log_event(
            None, LogLevel.CRITICAL, f"Failed to initialize database: {exc}", exc=exc
        )


initialize_database()
