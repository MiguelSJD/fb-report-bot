"""
Shared broadcasting logic for automated crons.
"""

import asyncio
import discord
from utils.server_settings import get_all_guild_channels
from utils.formatting import split_message_smartly
from models.log_level import LogLevel
from utils.logger import log_event


async def broadcast_report_to_servers(bot: discord.Client, report_data: str | list[str]):
    """Helper to send reports to all configured channels across all servers."""
    channel_ids = get_all_guild_channels()
    if not channel_ids:
        log_event(None, LogLevel.WARNING, "Broadcast skipped: No servers have configured a cron channel.")
        return

    messages = [report_data] if isinstance(report_data, str) else report_data

    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)

        if not channel:
            try:
                channel = await bot.fetch_channel(channel_id)
            except (discord.NotFound, discord.Forbidden):
                log_event(
                    None,
                    LogLevel.WARNING,
                    f"Unable to access configured channel {channel_id} (bot was kicked or channel was deleted)."
                )
                continue

        if not channel:
            continue

        guild_id = channel.guild.id if hasattr(channel, "guild") and channel.guild else None

        for msg in messages:
            chunks = split_message_smartly(msg)
            for chunk in chunks:
                try:
                    await channel.send(content=chunk)
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    log_event(
                        guild_id,
                        LogLevel.ERROR,
                        f"Missing permissions to send broadcast message in channel {channel_id}."
                    )
                except Exception as e:
                    log_event(
                        guild_id,
                        LogLevel.ERROR,
                        f"Failed to send broadcast to channel {channel_id}: {e}",
                        exc=e
                    )