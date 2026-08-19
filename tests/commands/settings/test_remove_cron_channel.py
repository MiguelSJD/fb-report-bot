"""
Unit tests for remove-cron-channel command handler logic.
"""

from unittest.mock import AsyncMock, patch

import pytest

from commands.settings.remove_cron_channel import handle_remove_cron_channel


@pytest.mark.asyncio
async def test_remove_cron_channel_success():
    """Test successful removal when a configuration exists."""
    interaction = AsyncMock()
    interaction.guild_id = 123456789
    interaction.user.guild_permissions.manage_guild = True

    with patch("commands.settings.remove_cron_channel.remove_cron_channel_config", return_value=1):
        await handle_remove_cron_channel(interaction, cron_type="daily-report")

        interaction.response.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_remove_cron_channel_not_found():
    """Test response when no cron channel was configured."""
    interaction = AsyncMock()
    interaction.guild_id = 123456789
    interaction.user.guild_permissions.manage_guild = True

    with patch("commands.settings.remove_cron_channel.remove_cron_channel_config", return_value=0):
        await handle_remove_cron_channel(interaction, cron_type="daily-report")

        interaction.response.send_message.assert_called_once()