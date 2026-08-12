"""
Unit tests for set-cron-channel command handler logic.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.set_cron_channel import handle_set_cron_channel


@pytest.mark.asyncio
async def test_set_cron_channel_success():
    """Test successful configuration of cron channel."""
    interaction = AsyncMock()
    interaction.guild_id = 123456789
    interaction.user.guild_permissions.manage_guild = True

    channel = MagicMock()
    channel.id = 987654321

    with patch("commands.set_cron_channel.set_guild_channel") as mock_set_db:
        await handle_set_cron_channel(interaction, channel)

        mock_set_db.assert_called_once_with(123456789, 987654321)
        interaction.response.send_message.assert_called_once()
        assert (
            "Successfully set"
            in interaction.response.send_message.call_args.kwargs["content"]
        )