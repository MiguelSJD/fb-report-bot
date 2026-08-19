"""
Slash command handler for removing cron report channel settings.
"""

import sqlite3
import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.settings_db import remove_cron_channel_config


async def handle_remove_cron_channel(
    interaction: discord.Interaction,
    cron_type: str,
    channel: discord.TextChannel | None = None,
) -> None:
    """Handle the remove-cron-channel slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None
    channel_id = channel.id if channel else None

    try:
        deleted_count = remove_cron_channel_config(
            guild_id=interaction.guild_id,
            cron_type=cron_type,
            channel_id=channel_id,
        )

        if deleted_count > 0:
            log_event(
                guild_id,
                LogLevel.INFO,
                f"User {interaction.user} removed {deleted_count} cron channel config(s) for '{cron_type}'.",
            )
            target_str = f"<#{channel_id}>" if channel_id else "all channels"
            await interaction.response.send_message(
                content=f"✅ Removed configuration for **`{cron_type}`** ({target_str}).",
                ephemeral=True,
            )
        else:
            log_event(
                guild_id,
                LogLevel.INFO,
                f"User {interaction.user} tried to remove config for '{cron_type}', but none existed.",
            )
            await interaction.response.send_message(
                content=f"ℹ️ No active configuration found for **`{cron_type}`**.",
                ephemeral=True,
            )
    except (
        sqlite3.Error,
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Failed to remove cron channel: {exc}", exc=exc
        )
        await interaction.response.send_message(
            content=f"❌ **Failed to remove cron channel**\n\n`{exc!s}`",
            ephemeral=True,
        )