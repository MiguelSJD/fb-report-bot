"""
Database connection and initialization helper for F&B Bot.
Manages database connection lifecycle and schema initialization.
"""

import os
import sqlite3
from contextlib import contextmanager

from config import DB_PATH
from models.log_level import LogLevel
from utils.logger import log_event
from utils.quiz_db import init_quiz_table
from utils.settings_db import init_settings_table

SCHEMA_INITIALIZERS = [
    init_settings_table,
    init_quiz_table,
]


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


initialize_database()
