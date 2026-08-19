"""
Shared broadcasting logic for automated crons.
"""

import asyncio

import discord

from models.log_level import LogLevel
from utils.formatting import split_message_smartly
from utils.logger import log_event
from utils.settings_db import get_cron_channels_by_type


async def broadcast_report_to_servers(
    bot: discord.Client,
    report_data: str | list[str],
    cron_type: str,
) -> None:
    """Helper to send reports and ping tags to all configured channels for a specific cron type."""
    channels_info = get_cron_channels_by_type(cron_type)
    if not channels_info:
        log_event(
            None,
            LogLevel.WARNING,
            f"Broadcast skipped: No servers have configured a channel for '{cron_type}'.",
        )
        return

    for guild_id, channel_id, tags in channels_info:
        channel = bot.get_channel(channel_id)

        if not channel:
            try:
                channel = await bot.fetch_channel(channel_id)
            except (discord.NotFound, discord.Forbidden):
                log_event(
                    guild_id,
                    LogLevel.WARNING,
                    f"Unable to access configured channel {channel_id} for '{cron_type}' "
                    "(bot was kicked or channel was deleted).",
                )
                continue

        if not channel:
            continue

        raw_messages = (
            [report_data] if isinstance(report_data, str) else list(report_data)
        )

        if tags and raw_messages:
            raw_messages[-1] = f"{raw_messages[-1]}\n\n{tags.strip()}"

        for msg in raw_messages:
            chunks = split_message_smartly(msg)
            for chunk in chunks:
                try:
                    await channel.send(content=chunk)
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    log_event(
                        guild_id,
                        LogLevel.ERROR,
                        f"Missing permissions to send '{cron_type}' broadcast in channel {channel_id}.",
                    )
                except (
                    discord.HTTPException,
                    discord.DiscordException,
                    OSError,
                ) as exc:
                    log_event(
                        guild_id,
                        LogLevel.ERROR,
                        f"Failed to send '{cron_type}' broadcast to channel {channel_id}: {exc}",
                        exc=exc,
                    )
