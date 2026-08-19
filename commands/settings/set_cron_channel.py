"""
Slash command handler for setting cron report channels.
"""

import sqlite3

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.settings_db import set_cron_channel_config


async def handle_set_cron_channel(
    interaction: discord.Interaction,
    cron_type: str,
    channel: discord.TextChannel,
    tags: str | None = None,
) -> None:
    """Handle the set-cron-channel slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None
    clean_tags = tags.strip() if tags else ""

    try:
        set_cron_channel_config(
            guild_id=interaction.guild_id,
            cron_type=cron_type,
            channel_id=channel.id,
            tags=clean_tags,
        )

        log_event(
            guild_id,
            LogLevel.INFO,
            f"User {interaction.user} mapped cron '{cron_type}' to <#{channel.id}> (Tags: '{clean_tags}').",
        )

        tags_display = f"\n**Tags:** {clean_tags}" if clean_tags else ""
        await interaction.response.send_message(
            content=(
                f"✅ Successfully registered <#{channel.id}> for **`{cron_type}`**."
                f"{tags_display}"
            ),
            ephemeral=True,
        )
    except (
        sqlite3.Error,
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Failed to set cron channel: {exc}", exc=exc
        )
        await interaction.response.send_message(
            content=f"❌ **Failed to configure cron channel**\n\n`{exc!s}`",
            ephemeral=True,
        )
