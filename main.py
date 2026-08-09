#!/usr/bin/env python3
"""
FB Report Bot — Core Application Bootstrapper
"""
import os
import sys
import asyncio
import discord
from discord.ext import commands

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config import DISCORD_TOKEN
from models.log_level import LogLevel
from utils.logger import log_event

if not DISCORD_TOKEN:
    log_event(None, LogLevel.CRITICAL, "DISCORD_TOKEN is missing from environment file.")
    raise EnvironmentError("DISCORD_TOKEN is missing from .env file.")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


async def main():
    try:
        log_event(None, LogLevel.INFO, "Starting FB Report Bot process...")

        cogs_dir = os.path.join(project_root, "cogs")
        if os.path.exists(cogs_dir):
            for root, _, files in os.walk(cogs_dir):
                for filename in files:
                    if filename.endswith(".py") and not filename.startswith("__"):
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, project_root)

                        extension = os.path.splitext(rel_path)[0].replace(os.sep, ".")

                        await bot.load_extension(extension)
                        log_event(None, LogLevel.INFO, f"Successfully loaded extension: {extension}")
        else:
            log_event(None, LogLevel.WARNING, "'cogs' directory not found. Skipping extension loading.")

        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        log_event(None, LogLevel.INFO, "Shutdown signal received (KeyboardInterrupt). Exiting gracefully.")
    except Exception as exc:
        log_event(None, LogLevel.CRITICAL, f"Fatal process error: {exc}", exc=exc)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        log_event(None, LogLevel.CRITICAL, f"Uncaught fatal error in event loop: {exc}", exc=exc)
        sys.exit(1)
