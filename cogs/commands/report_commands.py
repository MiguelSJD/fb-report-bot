"""
Slash commands for generating feedback reports.
"""

import discord
from discord import app_commands
from discord.ext import commands

from commands.report.daily_report import handle_daily_report
from commands.report.mid_week_report import handle_mid_week_report
from commands.report.weekly_report import handle_weekly_report_top_10
from utils.permissions import has_required_roles


class ReportCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="daily-report", description="Generate today's report for votes >= 50"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def daily_report(self, interaction: discord.Interaction):
        """Generates a daily report for the current date."""
        await handle_daily_report(interaction)

    @app_commands.command(
        name="mid-week-report", description="Generate mid-week report (non-empty days)"
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def mid_week_report(self, interaction: discord.Interaction):
        """Generates a mid-week report across multiple messages."""
        await handle_mid_week_report(interaction)

    @app_commands.command(
        name="weekly-report-top-10",
        description="Generate top 10 weekly feedback report",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @has_required_roles()
    async def weekly_report_top_10(self, interaction: discord.Interaction):
        """Generates a weekly top 10 feedback report across multiple messages."""
        await handle_weekly_report_top_10(interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReportCommandsCog(bot))
