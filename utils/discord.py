"""
Discord interaction, authentication, and messaging helpers.
"""

import asyncio

import discord

from config import ALLOWED_USER_IDS
from models.log_level import LogLevel
from utils.constants import DISCORD_RATE_LIMIT_DELAY
from utils.formatting import split_message_smartly
from utils.logger import log_event


def validate_interaction(interaction: discord.Interaction) -> tuple[bool, str]:
    """Ensures command is executed by an authorized user."""
    guild_id = interaction.guild_id if interaction.guild else None

    if ALLOWED_USER_IDS and interaction.user.id not in ALLOWED_USER_IDS:
        log_event(
            guild_id,
            LogLevel.WARNING,
            f"Unauthorized command attempt by user {interaction.user} (ID: {interaction.user.id}).",
        )
        return False, "⚠️ You do not have permission to execute this command."
    return True, ""


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
