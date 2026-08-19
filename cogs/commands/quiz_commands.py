"""
Discord Cog registering quiz app commands.
"""

import discord
from discord import app_commands
from discord.ext import commands

from commands.quiz.quiz import handle_quiz
from commands.quiz.quiz_add import handle_quiz_add
from commands.quiz.quiz_list import handle_quiz_list
from commands.quiz.quiz_remove import handle_quiz_remove
from utils.permissions import has_required_roles


class QuizCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="quiz", description="Generate and send a weekly quiz batch as a backup."
    )
    @app_commands.describe(tags="Optional role or user mentions (e.g., @Role)")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def quiz(self, interaction: discord.Interaction, tags: str | None = None):
        await handle_quiz(interaction, tags=tags)

    @app_commands.command(name="quiz-add", description="Add a new quiz question.")
    @app_commands.describe(question="The question text to add")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def quiz_add(self, interaction: discord.Interaction, question: str):
        await handle_quiz_add(interaction, question)

    @app_commands.command(
        name="quiz-list",
        description="List all quiz questions with interactive delete options.",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def quiz_list(self, interaction: discord.Interaction):
        await handle_quiz_list(interaction)

    @app_commands.command(
        name="quiz-remove", description="Remove a quiz question by ID."
    )
    @app_commands.describe(question_id="The UUID string of the question to remove")
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def quiz_remove(self, interaction: discord.Interaction, question_id: str):
        await handle_quiz_remove(interaction, question_id)


async def setup(bot: commands.Bot):
    await bot.add_cog(QuizCog(bot))
