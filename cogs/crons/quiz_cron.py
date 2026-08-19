"""
Background task for Weekly Quiz broadcasts.
"""

import asyncio
import datetime

import discord
from discord.ext import commands, tasks

from commands.quiz.quiz import generate_quiz_message
from models.log_level import LogLevel
from models.weekday import Weekday
from utils.broadcaster import broadcast_report_to_servers
from utils.constants import CRON_TYPE_CHOICES
from utils.logger import log_event

CRON_TIMES = [
    datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc),
]


class QuizCron(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.quiz_task.start()

    def cog_unload(self):
        self.quiz_task.cancel()

    @tasks.loop(time=CRON_TIMES)
    async def quiz_task(self):
        weekday = datetime.datetime.now(datetime.timezone.utc).weekday()

        if weekday != Weekday.MONDAY:
            return

        try:
            log_event(None, LogLevel.INFO, "Starting scheduled Quiz cron...")
            quiz_data = await asyncio.to_thread(lambda: generate_quiz_message())

            if quiz_data:
                await broadcast_report_to_servers(
                    self.bot, quiz_data, cron_type=CRON_TYPE_CHOICES["quiz"]
                )
                log_event(None, LogLevel.INFO, "Quiz cron completed successfully.")
            else:
                log_event(
                    None,
                    LogLevel.WARNING,
                    "Quiz cron skipped: Not enough questions found in database (minimum 5 required).",
                )
        except (discord.HTTPException, discord.DiscordException, OSError) as exc:
            log_event(
                None, LogLevel.ERROR, f"Quiz CRON Execution Error: {exc}", exc=exc
            )

    @quiz_task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(QuizCron(bot))
