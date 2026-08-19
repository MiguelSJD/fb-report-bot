"""
Slash command handler for adding a quiz question.
"""

import sqlite3

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.quiz_db import add_question


async def handle_quiz_add(interaction: discord.Interaction, question: str) -> None:
    """Handle the /quiz-add slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        question_id = add_question(guild_id, question)
        log_event(
            guild_id,
            LogLevel.INFO,
            f"User {interaction.user} added quiz question: {question_id}",
        )
        await interaction.response.send_message(
            f"✅ Question added successfully!\n**ID:** `{question_id}`\n**Question:** {question}",
            ephemeral=True,
        )
    except (
        sqlite3.Error,
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Failed to add quiz question: {exc}", exc=exc
        )
        await interaction.response.send_message(
            f"❌ Failed to add question: `{exc}`", ephemeral=True
        )
