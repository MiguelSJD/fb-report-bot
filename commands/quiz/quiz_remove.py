"""
Slash command handler for removing a quiz question by ID.
"""

import sqlite3

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.quiz_db import remove_question


async def handle_quiz_remove(
    interaction: discord.Interaction, question_id: str
) -> None:
    """Handle the /quiz-remove slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        deleted = remove_question(question_id)
        if deleted:
            log_event(
                guild_id,
                LogLevel.INFO,
                f"User {interaction.user} removed quiz question: {question_id}",
            )
            await interaction.response.send_message(
                f"✅ Successfully deleted question `{question_id}`.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ No question found with ID `{question_id}`.", ephemeral=True
            )
    except (
        sqlite3.Error,
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Failed to remove quiz question: {exc}", exc=exc
        )
        await interaction.response.send_message(
            f"❌ Error deleting question: `{exc}`", ephemeral=True
        )
