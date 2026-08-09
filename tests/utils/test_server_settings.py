"""
Unit tests for server settings database CRUD operations using in-memory SQLite.
"""

import sqlite3
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from utils.server_settings import (
    get_all_guild_channels,
    get_guild_channel,
    remove_guild_channel,
    set_guild_channel,
)


@pytest.fixture
def mock_db():
    """Provides an in-memory SQLite connection pre-populated with schema."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE guild_channels
        (
            guild_id   INTEGER PRIMARY KEY,
            channel_id INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()

    @contextmanager
    def _get_test_db():
        yield conn

    with (
        patch("utils.server_settings.get_db_connection", _get_test_db),
        patch("utils.database.get_db_connection", _get_test_db),
    ):
        yield conn

    conn.close()


def test_set_and_get_guild_channel(mock_db):
    guild_id = 1111
    channel_id = 2222

    set_guild_channel(guild_id, channel_id)
    assert get_guild_channel(guild_id) == channel_id


def test_upsert_guild_channel(mock_db):
    guild_id = 1111
    set_guild_channel(guild_id, 2222)
    set_guild_channel(guild_id, 3333)

    assert get_guild_channel(guild_id) == 3333


def test_remove_guild_channel(mock_db):
    guild_id = 1111
    set_guild_channel(guild_id, 2222)

    assert remove_guild_channel(guild_id) is True
    assert get_guild_channel(guild_id) is None
    assert remove_guild_channel(guild_id) is False


def test_get_all_guild_channels(mock_db):
    set_guild_channel(1, 100)
    set_guild_channel(2, 200)

    channels = get_all_guild_channels()
    assert sorted(channels) == [100, 200]
