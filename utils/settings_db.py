"""
Database helper functions for F&B Bot server settings.
Contains all CRUD operations for guild cron configurations.
"""

import sqlite3

from utils.database import get_db_connection


def init_settings_table(cursor: sqlite3.Cursor) -> None:
    """Creates the cron_jobs table if it doesn't exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cron_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            cron_type TEXT NOT NULL,
            channel_id INTEGER NOT NULL,
            tags TEXT DEFAULT '',
            schedule_cron TEXT DEFAULT '0 12 * * *',
            timezone TEXT DEFAULT 'UTC',
            is_enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(guild_id, cron_type, channel_id)
        )
        """
    )


def set_cron_channel_config(
    guild_id: int, cron_type: str, channel_id: int, tags: str = ""
) -> None:
    """Upsert a specific cron job configuration for a guild."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO cron_jobs (guild_id, cron_type, channel_id, tags, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(guild_id, cron_type, channel_id) DO UPDATE SET
                tags = excluded.tags,
                updated_at = CURRENT_TIMESTAMP
            """,
            (guild_id, cron_type, channel_id, tags),
        )
        conn.commit()


def remove_cron_channel_config(
    guild_id: int, cron_type: str, channel_id: int | None = None
) -> int:
    """
    Remove cron job configurations for a guild.
    If channel_id is provided, removes only that specific mapping.
    Otherwise, removes ALL jobs registered under that cron_type.
    Returns the number of deleted rows.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if channel_id:
            cursor.execute(
                "DELETE FROM cron_jobs WHERE guild_id = ? AND cron_type = ? AND channel_id = ?",
                (guild_id, cron_type, channel_id),
            )
        else:
            cursor.execute(
                "DELETE FROM cron_jobs WHERE guild_id = ? AND cron_type = ?",
                (guild_id, cron_type),
            )
        conn.commit()
        return cursor.rowcount


def get_cron_channels_by_type(cron_type: str) -> list[tuple[int, int, str]]:
    """
    Fetch all active enabled channels configured for a specific cron job across all guilds.
    Returns a list of tuples: (guild_id, channel_id, tags)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT guild_id, channel_id, tags 
            FROM cron_jobs 
            WHERE cron_type = ? AND is_enabled = 1
            """,
            (cron_type,),
        )
        return cursor.fetchall()


def get_guild_cron_configs(guild_id: int) -> list[tuple[str, int, str]]:
    """
    Fetch all cron configurations for a specific guild.
    Returns a list of tuples: (cron_type, channel_id, tags)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT cron_type, channel_id, tags 
            FROM cron_jobs 
            WHERE guild_id = ? AND is_enabled = 1 
            ORDER BY cron_type
            """,
            (guild_id,),
        )
        return cursor.fetchall()