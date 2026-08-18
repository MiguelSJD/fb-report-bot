"""
Database helper functions for F&B Bot server settings.
Contains all CRUD operations for guild channel configurations.
"""

from utils.database import get_db_connection


def set_guild_channel(guild_id: int, channel_id: int) -> None:
    """
    Upsert the channel ID for a guild.
    Uses INSERT OR REPLACE to update if exists, insert if not.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO guild_channels (guild_id, channel_id, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (guild_id, channel_id),
        )
        conn.commit()


def get_guild_channel(guild_id: int) -> int | None:
    """
    Get the channel ID for a guild.
    Returns None if not set.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT channel_id FROM guild_channels WHERE guild_id = ?",
            (guild_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def remove_guild_channel(guild_id: int) -> bool:
    """
    Remove the channel setting for a guild.
    Returns True if a row was deleted, False if nothing was removed.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM guild_channels WHERE guild_id = ?",
            (guild_id,),
        )
        conn.commit()
        return cursor.rowcount > 0


def get_all_guild_channels() -> list[int]:
    """
    Fetch all configured cron channels from the database.
    Returns a list of channel IDs.
    """
    from utils.database import get_db_connection

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id FROM guild_channels")
        return [row[0] for row in cursor.fetchall()]
