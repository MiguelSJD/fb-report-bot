"""
Slash command handler for removing the cron report channel setting.
"""

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.server_settings import remove_guild_channel


async def handle_remove_cron_channel(interaction: discord.Interaction):
    """Handle the remove-cron-channel slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        if remove_guild_channel(interaction.guild_id):
            log_event(
                guild_id,
                LogLevel.INFO,
                f"User {interaction.user} removed the cron channel configuration for this guild.",
            )
            await interaction.response.send_message(
                content="✅ Removed the cron report channel configuration for this server.",
                ephemeral=True,
            )
        else:
            log_event(
                guild_id,
                LogLevel.INFO,
                f"User {interaction.user} tried to remove cron channel, but none was configured.",
            )
            await interaction.response.send_message(
                content="ℹ️ No cron channel is currently configured for this server. Use `/set-cron-channel` to configure one.",
                ephemeral=True,
            )
    except (
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Failed to remove cron channel: {exc}", exc=exc
        )
        error_msg = f"❌ **Failed to remove cron channel**\n\n`{exc!s}`"
        await interaction.response.send_message(content=error_msg, ephemeral=True)
