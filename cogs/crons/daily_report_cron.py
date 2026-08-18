"""
Background task for Daily FB Report broadcasts.
"""

import asyncio
import datetime

import discord
from discord.ext import commands, tasks

from commands.daily_report import generate_daily_report
from models.log_level import LogLevel
from models.weekday import Weekday
from utils.broadcaster import broadcast_report_to_servers
from utils.google_sheets import get_report_worksheet
from utils.logger import log_event

CRON_TIMES = [
    datetime.time(hour=12, minute=0, tzinfo=datetime.timezone.utc),
    datetime.time(hour=23, minute=30, tzinfo=datetime.timezone.utc),
]


class DailyReportCron(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    @tasks.loop(time=CRON_TIMES)
    async def daily_task(self):
        weekday = datetime.datetime.now(datetime.timezone.utc).weekday()

        if weekday not in [
            Weekday.MONDAY,
            Weekday.TUESDAY,
            Weekday.THURSDAY,
            Weekday.FRIDAY,
            Weekday.SUNDAY,
        ]:
            return

        try:
            log_event(None, LogLevel.INFO, "Starting scheduled Daily Report cron...")
            worksheet = get_report_worksheet()
            report_data = await asyncio.to_thread(
                lambda: generate_daily_report(worksheet)
            )

            if report_data:
                await broadcast_report_to_servers(self.bot, report_data)
                log_event(
                    None, LogLevel.INFO, "Daily Report cron completed successfully."
                )
        except (discord.HTTPException, discord.DiscordException, OSError) as exc:
            log_event(
                None, LogLevel.ERROR, f"Daily CRON Execution Error: {exc}", exc=exc
            )

    @daily_task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(DailyReportCron(bot))
