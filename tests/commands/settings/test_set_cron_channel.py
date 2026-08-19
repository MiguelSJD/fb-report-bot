"""
Unit tests for set-cron-channel command handler logic.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.settings.set_cron_channel import handle_set_cron_channel


@pytest.mark.asyncio
async def test_set_cron_channel_success():
    """Test successful configuration of cron channel."""
    interaction = AsyncMock()
    interaction.guild_id = 123456789
    interaction.user.guild_permissions.manage_guild = True

    channel = MagicMock()
    channel.id = 987654321

    with patch("commands.settings.set_cron_channel.set_cron_channel_config") as mock_set_db:
        await handle_set_cron_channel(interaction, "daily-report", channel, tags="<@&123>")

        mock_set_db.assert_called_once_with(
            guild_id=123456789,
            cron_type="daily-report",
            channel_id=987654321,
            tags="<@&123>",
        )
        interaction.response.send_message.assert_called_once()