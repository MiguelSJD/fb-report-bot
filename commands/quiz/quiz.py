"""
Quiz generator module for F&B Bot.
"""

import asyncio
import sqlite3

import discord

from models.log_level import LogLevel
from utils.logger import log_event
from utils.quiz_db import fetch_and_rotate_quiz_questions


def generate_quiz_message(channel_mention: str | None = None) -> str | None:
    """
    Fetches 5 questions and formats the quiz broadcast message.
    Returns None if fewer than 5 total questions exist in the database.
    """
    questions = fetch_and_rotate_quiz_questions()
    if not questions:
        return None

    target_channel = channel_mention or "#weekly-quiz"
    formatted_questions = "\n".join(
        f"{idx}. {q_text}" for idx, q_text in enumerate(questions, start=1)
    )

    return (
        f"# 🧩 Welcome to our weekly Quiz\n"
        f"Answer the following by submitting your answers to {target_channel} channel before **Monday 00:00 UTC**.\n\n"
        f"{formatted_questions}"
    )


async def handle_quiz(
    interaction: discord.Interaction, tags: str | None = None
) -> None:
    """Handle the /quiz backup slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        log_event(guild_id, LogLevel.INFO, f"User {interaction.user} triggered /quiz")
        await interaction.response.defer(ephemeral=False)

        channel_mention = f"<#{interaction.channel_id}>"
        quiz_body = await asyncio.to_thread(
            lambda: generate_quiz_message(channel_mention)
        )

        if not quiz_body:
            # Log for the slash command attempt as well
            log_event(
                guild_id,
                LogLevel.WARNING,
                f"Quiz generation failed for /quiz by {interaction.user}: Not enough questions found (minimum 5 required).",
            )
            await interaction.followup.send(
                content="❌ **Not enough questions found.** At least 5 questions are required in the database.",
                ephemeral=True,
            )
            return

        final_message = f"{quiz_body}\n\n{tags.strip()}" if tags else quiz_body
        await interaction.followup.send(content=final_message)

    except (
        sqlite3.Error,
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(guild_id, LogLevel.ERROR, f"Quiz generation failed: {exc}", exc=exc)
        await interaction.followup.send(content=f"❌ Error: {exc}", ephemeral=True)