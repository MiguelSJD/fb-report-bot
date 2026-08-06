"""
Discord interaction and messaging helpers.
"""

import asyncio
import discord
from utils.formatting import split_message_smartly

DISCORD_RATE_LIMIT_DELAY = 0.5

async def send_report_response(interaction: discord.Interaction, report_data: str | list[str]):
    """
    Handles sending single or multi-part reports to Discord without hitting length limits.
    Sends the first block as an interaction followup and subsequent blocks to the channel.
    """
    messages = [report_data] if isinstance(report_data, str) else report_data

    if not messages:
        await interaction.followup.send(content="No report data generated.")
        return

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