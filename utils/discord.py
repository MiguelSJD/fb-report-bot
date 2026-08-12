"""
Discord interaction, authentication, and messaging helpers.
"""

import asyncio
import time

import discord
from gspread.exceptions import GSpreadException

from models.log_level import LogLevel
from utils.constants import DISCORD_RATE_LIMIT_DELAY, SHEET_UPDATE_DELAY, TRIGGER_CELL
from utils.formatting import split_message_smartly
from utils.logger import log_event


def trigger_sheet_update(worksheet, lookback_days: str) -> None:
    """Updates the worksheet's trigger cell with lookback days and waits for backend processing."""
    try:
        worksheet.update_acell(TRIGGER_CELL, lookback_days)
        time.sleep(SHEET_UPDATE_DELAY)
    except GSpreadException as exc:
        log_event(
            None,
            LogLevel.WARNING,
            f"Failed to update trigger cell {TRIGGER_CELL}: {exc}",
            exc=exc,
        )


async def send_report_response(
    interaction: discord.Interaction, report_data: str | list[str]
):
    """
    Handles sending single or multi-part reports to Discord without hitting length limits.
    Sends the first block as an interaction followup and subsequent blocks to the channel.
    """
    guild_id = interaction.guild_id if interaction.guild else None
    messages = [report_data] if isinstance(report_data, str) else report_data

    if not messages:
        log_event(
            guild_id,
            LogLevel.WARNING,
            "send_report_response received empty report data.",
        )
        await interaction.followup.send(content="No report data generated.")
        return

    try:
        first_msg = messages[0]
        first_chunks = split_message_smartly(first_msg)
        await interaction.followup.send(content=first_chunks[0], ephemeral=False)

        for chunk in first_chunks[1:]:
            await asyncio.sleep(DISCORD_RATE_LIMIT_DELAY)
            await interaction.channel.send(content=chunk)

        for msg in messages[1:]:
            await asyncio.sleep(DISCORD_RATE_LIMIT_DELAY)
            chunks = split_message_smartly(msg)
            for chunk in chunks:
                await interaction.channel.send(content=chunk)

        log_event(
            guild_id,
            LogLevel.INFO,
            f"Successfully delivered report response ({len(messages)} block(s)).",
        )

    except discord.Forbidden:
        log_event(
            guild_id,
            LogLevel.ERROR,
            "Failed to send report response: Bot lacks permission to post in channel.",
        )
        raise
    except Exception as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Error sending report response: {exc}", exc=exc
        )
        raise


async def handle_report_error(
    interaction: discord.Interaction,
    exc: Exception,
    guild_id: int | None,
    log_message: str,
) -> None:
    """Logs report command exceptions and alerts the user with an ephemeral message."""
    log_event(
        guild_id,
        LogLevel.ERROR,
        f"{log_message}: {exc}",
        exc=exc,
    )
    error_msg = f"❌ **Report generation failed**\n\n`{exc!s}`"
    if interaction.response.is_done():
        await interaction.followup.send(content=error_msg, ephemeral=True)
    else:
        await interaction.response.send_message(content=error_msg, ephemeral=True)
