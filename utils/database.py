"""
Database connection lifecycle helper.
"""

import os
import sqlite3
from contextlib import contextmanager

from config import DB_PATH
from models.log_level import LogLevel
from utils.logger import log_event


def ensure_db_directory() -> None:
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