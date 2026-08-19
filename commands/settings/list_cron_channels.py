"""
Slash command handler for listing all configured cron channels for a server.
"""

import sqlite3

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.settings_db import get_guild_cron_configs
from utils.settings_helper import CronChannelsListView


async def handle_list_cron_channels(
    interaction: discord.Interaction, cron_type: str | None = None
) -> None:
    """Handle the list-cron-channels slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        configs = get_guild_cron_configs(interaction.guild_id)

        if cron_type:
            configs = [c for c in configs if c[0] == cron_type]

        if not configs:
            msg = (
                f"ℹ️ No cron report channels are configured for **`{cron_type}`**."
                if cron_type
                else "ℹ️ No cron report channels are currently configured for this server."
            )
            await interaction.response.send_message(
                content=msg,
                ephemeral=True,
            )
            return

        view = CronChannelsListView(
            guild_id=interaction.guild_id,
            configs=configs,
            filter_cron_type=cron_type,
        )
        await interaction.response.send_message(
            embed=view.build_embed(), view=view, ephemeral=True
        )
    except (
        sqlite3.Error,
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Failed to list cron channels: {exc}", exc=exc
        )
        await interaction.response.send_message(
            content=f"❌ **Failed to fetch cron channels**\n\n`{exc!s}`",
            ephemeral=True,
        )
