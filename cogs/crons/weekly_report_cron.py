"""
Background task for Weekly Top 10 FB Report broadcasts.
"""

import asyncio
import datetime

import discord
from discord.ext import commands, tasks

from commands.weekly_report import generate_weekly_top_10_report
from models.log_level import LogLevel
from models.weekday import Weekday
from utils.broadcaster import broadcast_report_to_servers
from utils.google_sheets import get_worksheet
from utils.logger import log_event

CRON_TIMES = [
    datetime.time(hour=12, minute=0, tzinfo=datetime.timezone.utc),
    datetime.time(hour=23, minute=30, tzinfo=datetime.timezone.utc),
]


class WeeklyReportCron(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.weekly_task.start()

    def cog_unload(self):
        self.weekly_task.cancel()

    @tasks.loop(time=CRON_TIMES)
    async def weekly_task(self):
        weekday = datetime.datetime.now(datetime.timezone.utc).weekday()

        if weekday != Weekday.SATURDAY:
            return

        try:
            log_event(
                None, LogLevel.INFO, "Starting scheduled Weekly Top 10 Report cron..."
            )
            worksheet = get_worksheet()
            report_data = await asyncio.to_thread(
                lambda: generate_weekly_top_10_report(worksheet)
            )

            if report_data:
                await broadcast_report_to_servers(self.bot, report_data)
                log_event(
                    None,
                    LogLevel.INFO,
                    "Weekly Top 10 Report cron completed successfully.",
                )
        except (discord.HTTPException, discord.DiscordException, OSError) as exc:
            log_event(
                None, LogLevel.ERROR, f"Weekly CRON Execution Error: {exc}", exc=exc
            )

    @weekly_task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(WeeklyReportCron(bot))
