"""
Unit tests for remove-cron-channel command handler logic.
"""

import pytest
from unittest.mock import AsyncMock, patch
from commands.remove_cron_channel import handle_remove_cron_channel


@pytest.mark.asyncio
async def test_remove_cron_channel_success():
    """Test successful removal when a configuration exists."""
    interaction = AsyncMock()
    interaction.guild_id = 123456789
    interaction.user.guild_permissions.manage_guild = True

    with patch("commands.remove_cron_channel.validate_interaction", return_value=(True, "")), \
         patch("commands.remove_cron_channel.remove_guild_channel", return_value=True):

        await handle_remove_cron_channel(interaction)

        interaction.response.send_message.assert_called_once()
        assert "Removed the cron report channel" in interaction.response.send_message.call_args.kwargs["content"]


@pytest.mark.asyncio
async def test_remove_cron_channel_not_found():
    """Test response when no cron channel was configured."""
    interaction = AsyncMock()
    interaction.guild_id = 123456789
    interaction.user.guild_permissions.manage_guild = True

    with patch("commands.remove_cron_channel.validate_interaction", return_value=(True, "")), \
         patch("commands.remove_cron_channel.remove_guild_channel", return_value=False):

        await handle_remove_cron_channel(interaction)

        interaction.response.send_message.assert_called_once()
        assert "No cron channel is currently configured" in interaction.response.send_message.call_args.kwargs["content"]