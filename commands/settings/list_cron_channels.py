"""
Slash command handler for listing all configured cron channels for a server.
"""

import sqlite3

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.settings_db import get_guild_cron_configs


async def handle_list_cron_channels(interaction: discord.Interaction) -> None:
    """Handle the list-cron-channels slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        configs = get_guild_cron_configs(interaction.guild_id)
        if not configs:
            await interaction.response.send_message(
                content="ℹ️ No cron report channels are currently configured for this server.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="⚙️ Configured Cron Channels",
            color=discord.Color.blue(),
        )

        for cron_type, channel_id, tags in configs:
            tags_str = f" | Tags: `{tags}`" if tags else ""
            embed.add_field(
                name=f"📌 {cron_type}",
                value=f"Channel: <#{channel_id}>{tags_str}",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)
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
