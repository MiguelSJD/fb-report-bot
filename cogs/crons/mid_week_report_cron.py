"""
Background task for Mid-Week Feedback Report broadcasts.
"""

import asyncio
import datetime

import discord
from discord.ext import commands, tasks

from commands.report.mid_week_report import generate_mid_week_report
from models.log_level import LogLevel
from models.weekday import Weekday
from utils.broadcaster import broadcast_report_to_servers
from utils.google_sheets import get_report_worksheet
from utils.logger import log_event

CRON_TIMES = [
    datetime.time(hour=12, minute=0, tzinfo=datetime.timezone.utc),
    datetime.time(hour=23, minute=30, tzinfo=datetime.timezone.utc),
]


class MidWeekReportCron(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mid_week_task.start()

    def cog_unload(self):
        self.mid_week_task.cancel()

    @tasks.loop(time=CRON_TIMES)
    async def mid_week_task(self):
        weekday = datetime.datetime.now(datetime.timezone.utc).weekday()

        if weekday != Weekday.WEDNESDAY:
            return

        try:
            log_event(None, LogLevel.INFO, "Starting scheduled Mid-Week Report cron...")
            worksheet = get_report_worksheet()
            report_data = await asyncio.to_thread(
                lambda: generate_mid_week_report(worksheet)
            )

            if report_data:
                await broadcast_report_to_servers(self.bot, report_data)
                log_event(
                    None, LogLevel.INFO, "Mid-Week Report cron completed successfully."
                )
        except (discord.HTTPException, discord.DiscordException, OSError) as exc:
            log_event(
                None, LogLevel.ERROR, f"Mid-Week CRON Execution Error: {exc}", exc=exc
            )

    @mid_week_task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(MidWeekReportCron(bot))
