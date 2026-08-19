"""
Slash commands for moderator activity reports.
"""

import discord
from discord import app_commands
from discord.ext import commands

from commands.activity.activity_report import handle_activity_report
from utils.permissions import has_required_roles


class ActivityCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="activity", description="📊 View a mod’s activity report"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def activity(self, interaction: discord.Interaction, user: discord.Member):
        """View a moderator's activity report and send it via DM."""
        await interaction.response.defer(ephemeral=True)
        await handle_activity_report(interaction, user)


async def setup(bot: commands.Bot):
    await bot.add_cog(ActivityCommandsCog(bot))
