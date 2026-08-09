"""
Slash command handler for removing the cron report channel setting.
"""

import discord
from utils.server_settings import remove_guild_channel
from utils.discord import validate_interaction
from models.log_level import LogLevel
from utils.logger import log_event


async def handle_remove_cron_channel(interaction: discord.Interaction):
    """Handle the remove-cron-channel slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None
    is_valid, error_msg = validate_interaction(interaction)
    if not is_valid:
        log_event(guild_id, LogLevel.WARNING, f"Invalid remove-cron-channel interaction: {error_msg}")
        await interaction.response.send_message(content=error_msg, ephemeral=True)
        return

    if not interaction.user.guild_permissions.manage_guild:
        log_event(
            guild_id,
            LogLevel.WARNING,
            f"User {interaction.user} attempted to remove cron channel without 'Manage Server' permission."
        )
        await interaction.response.send_message(
            content="⚠️ You need the 'Manage Server' permission to use this command.",
            ephemeral=True
        )
        return

    try:
        if remove_guild_channel(interaction.guild_id):
            log_event(
                guild_id,
                LogLevel.INFO,
                f"User {interaction.user} removed the cron channel configuration for this guild."
            )
            await interaction.response.send_message(
                content="✅ Removed the cron report channel configuration for this server.",
                ephemeral=True
            )
        else:
            log_event(
                guild_id,
                LogLevel.INFO,
                f"User {interaction.user} tried to remove cron channel, but none was configured."
            )
            await interaction.response.send_message(
                content="ℹ️ No cron channel is currently configured for this server. Use `/set-cron-channel` to configure one.",
                ephemeral=True
            )
    except Exception as e:
        log_event(guild_id, LogLevel.ERROR, f"Failed to remove cron channel: {e}", exc=e)
        error_msg = f"❌ **Failed to remove cron channel**\n\n`{str(e)}`"
        await interaction.response.send_message(content=error_msg, ephemeral=True)