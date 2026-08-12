"""
Slash command handler for setting the cron report channel.
"""

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.server_settings import set_guild_channel


async def handle_set_cron_channel(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    """Handle the set-cron-channel slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        set_guild_channel(interaction.guild_id, channel.id)
        log_event(
            guild_id,
            LogLevel.INFO,
            f"User {interaction.user} set cron channel to <#{channel.id}> (ID: {channel.id}).",
        )
        await interaction.response.send_message(
            content=f"✅ Successfully set <#{channel.id}> as the cron report channel for this server.",
            ephemeral=True,
        )
    except (
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Failed to set cron channel: {exc}", exc=exc
        )
        error_msg = f"❌ **Failed to set cron channel**\n\n`{exc!s}`"
        await interaction.response.send_message(content=error_msg, ephemeral=True)
