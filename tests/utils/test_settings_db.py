"""
Unit tests for server settings database CRUD operations using in-memory SQLite.
"""

import sqlite3
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from utils.settings_db import (
    get_cron_channels_by_type,
    get_guild_cron_configs,
    init_settings_table,
    remove_cron_channel_config,
    set_cron_channel_config,
)


@pytest.fixture
def mock_db():
    """Provides an in-memory SQLite connection pre-populated with schema."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    init_settings_table(cursor)
    conn.commit()

    @contextmanager
    def _get_test_db():
        yield conn

    with (
        patch("utils.settings_db.get_db_connection", _get_test_db),
        patch("utils.database.get_db_connection", _get_test_db),
    ):
        yield conn

    conn.close()


def test_set_and_get_cron_channels_by_type(mock_db):
    set_cron_channel_config(
        guild_id=1111, cron_type="daily-report", channel_id=2222, tags="<@&123>"
    )
    set_cron_channel_config(
        guild_id=3333, cron_type="daily-report", channel_id=4444, tags=""
    )

    results = get_cron_channels_by_type("daily-report")
    assert len(results) == 2
    assert (1111, 2222, "<@&123>") in results
    assert (3333, 4444, "") in results


def test_upsert_cron_channel_config(mock_db):
    set_cron_channel_config(
        guild_id=1111, cron_type="weekly-report", channel_id=2222, tags="old_tag"
    )
    set_cron_channel_config(
        guild_id=1111, cron_type="weekly-report", channel_id=2222, tags="new_tag"
    )

    configs = get_guild_cron_configs(1111)
    assert len(configs) == 1
    assert configs[0] == ("weekly-report", 2222, "new_tag")


def test_remove_specific_cron_channel_config(mock_db):
    set_cron_channel_config(1111, "quiz", 2222)
    set_cron_channel_config(1111, "quiz", 3333)

    removed = remove_cron_channel_config(1111, "quiz", channel_id=2222)
    assert removed == 1

    remaining = get_guild_cron_configs(1111)
    assert len(remaining) == 1
    assert remaining[0][1] == 3333


def test_remove_all_channels_for_cron_type(mock_db):
    set_cron_channel_config(1111, "mid-week-report", 2222)
    set_cron_channel_config(1111, "mid-week-report", 3333)

    removed = remove_cron_channel_config(1111, "mid-week-report")
    assert removed == 2
    assert len(get_guild_cron_configs(1111)) == 0


def test_get_guild_cron_configs(mock_db):
    set_cron_channel_config(1111, "daily-report", 100, "tag1")
    set_cron_channel_config(1111, "quiz", 200, "tag2")

    configs = get_guild_cron_configs(1111)
    assert len(configs) == 2
    assert configs[0] == ("daily-report", 100, "tag1")
    assert configs[1] == ("quiz", 200, "tag2")
