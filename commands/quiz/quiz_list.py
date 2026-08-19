"""
Slash command handler for listing quiz questions with interactive delete options.
"""

import sqlite3

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.quiz_db import get_all_questions
from utils.quiz_helper import QuizListView


async def handle_quiz_list(interaction: discord.Interaction) -> None:
    """Handle the /quiz-list slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        questions = get_all_questions()
        if not questions:
            await interaction.response.send_message(
                "📝 **Quiz Questions List:**\n*No questions found.*",
                ephemeral=True,
            )
            return

        content = "📝 **Quiz Questions List:**\n\n" + "\n".join(
            f"• `{q_id[:8]}`: {text} *(Full ID: `{q_id}`)*" for q_id, text in questions
        )
        view = QuizListView(questions)
        await interaction.response.send_message(
            content=content, view=view, ephemeral=True
        )
    except (
        sqlite3.Error,
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Failed to list quiz questions: {exc}", exc=exc
        )
        await interaction.response.send_message(
            f"❌ Failed to fetch questions: `{exc}`", ephemeral=True
        )
