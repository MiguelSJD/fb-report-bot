"""
Background task for Weekly Quiz broadcasts.
"""

import datetime

import discord
from discord.ext import commands, tasks

from commands.quiz.quiz import generate_quiz_message
from models.log_level import LogLevel
from models.weekday import Weekday
from utils.broadcaster import broadcast_quiz_per_server
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

            cron_type_val = next(
                (c.value for c in CRON_TYPE_CHOICES if c.name.lower() == "quiz"),
                "quiz",
            )

            await broadcast_quiz_per_server(
                self.bot,
                quiz_generator_fn=generate_quiz_message,
                cron_type=cron_type_val,
            )
            log_event(None, LogLevel.INFO, "Quiz cron completed successfully.")
        except (discord.HTTPException, discord.DiscordException, OSError) as exc:
            log_event(
                None, LogLevel.ERROR, f"Quiz CRON Execution Error: {exc}", exc=exc
            )

    @quiz_task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(QuizCron(bot))
