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
        questions = get_all_questions(guild_id)
        if not questions:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="📝 Quiz Questions List",
                    description="*No questions found.*",
                    color=discord.Color.blue(),
                ),
                ephemeral=True,
            )
            return

        view = QuizListView(guild_id, questions)
        embed = view.build_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
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
