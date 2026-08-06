#!/usr/bin/env python3
"""
FB Report Bot — Discord Interface
"""

import os
import sys
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Add project directory to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

load_dotenv()

from commands.daily_report import generate_daily_report
from commands.mid_week_report import generate_mid_week_report
from commands.weekly_report import generate_weekly_top_10_report
from utils.google_sheets import get_worksheet
from utils.discord import send_report_response

# ── Configuration Constants ────────────────────────────────────
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

raw_user_ids = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS = [
    int(uid.strip()) for uid in raw_user_ids.split(",") if uid.strip().isdigit()
]

if not BOT_TOKEN:
    raise EnvironmentError("DISCORD_TOKEN is missing from .env file.")

# ── Bot Instance ───────────────────────────────────────────────
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def validate_interaction(interaction: discord.Interaction) -> tuple[bool, str]:
    """Ensures command is executed by an authorized user."""
    if ALLOWED_USER_IDS and interaction.user.id not in ALLOWED_USER_IDS:
        return False, "⚠️ You do not have permission to execute this command."
    return True, ""


# ── Slash Command: /daily-report ───────────────────────────────
@bot.tree.command(name="daily-report", description="Generate today's report for votes >= 50")
@app_commands.guild_only()
async def daily_report(interaction: discord.Interaction):
    """Generates a daily report for the current date."""
    is_valid, error_msg = validate_interaction(interaction)
    if not is_valid:
        await interaction.response.send_message(content=error_msg, ephemeral=True)
        return

    try:
        await interaction.response.defer(ephemeral=False)
        report_text = await asyncio.to_thread(lambda: generate_daily_report(get_worksheet()))
        await send_report_response(interaction, report_text)

    except Exception as e:
        print(f"Daily report error: {e}")
        error_msg = f"❌ **Report generation failed**\n\n`{str(e)}`"
        await interaction.followup.send(content=error_msg, ephemeral=True)


# ── Slash Command: /mid-week-report ─────────────────────────────
@bot.tree.command(name="mid-week-report", description="Generate mid-week report (non-empty days)")
@app_commands.guild_only()
async def mid_week_report(interaction: discord.Interaction):
    """Generates a mid-week report across multiple messages."""
    is_valid, error_msg = validate_interaction(interaction)
    if not is_valid:
        await interaction.response.send_message(content=error_msg, ephemeral=True)
        return

    try:
        await interaction.response.defer(ephemeral=False)
        report_messages = await asyncio.to_thread(lambda: generate_mid_week_report(get_worksheet()))
        await send_report_response(interaction, report_messages)

    except Exception as e:
        print(f"Mid-week report error: {e}")
        error_msg = f"❌ **Report generation failed**\n\n`{str(e)}`"
        if interaction.response.is_done():
            await interaction.followup.send(content=error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(content=error_msg, ephemeral=True)


# ── Slash Command: /weekly-report-top-10 ───────────────────────
@bot.tree.command(name="weekly-report-top-10", description="Generate top 10 weekly feedback report")
@app_commands.guild_only()
async def weekly_report_top_10(interaction: discord.Interaction):
    """Generates a weekly top 10 feedback report across multiple messages."""
    is_valid, error_msg = validate_interaction(interaction)
    if not is_valid:
        await interaction.response.send_message(content=error_msg, ephemeral=True)
        return

    try:
        await interaction.response.defer(ephemeral=False)
        report_messages = await asyncio.to_thread(lambda: generate_weekly_top_10_report(get_worksheet()))
        await send_report_response(interaction, report_messages)

    except Exception as e:
        print(f"Weekly top 10 report error: {e}")
        error_msg = f"❌ **Report generation failed**\n\n`{str(e)}`"
        if interaction.response.is_done():
            await interaction.followup.send(content=error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(content=error_msg, ephemeral=True)


# ── Error Handler ──────────────────────────────────────────────
@bot.tree.error
async def on_tree_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CheckFailure):
        msg = "⚠️ You don't have permission to use this command."
    elif isinstance(error, discord.app_commands.CommandNotFound):
        msg = "⚠️ This command is not available in this channel."
    else:
        print(f"App command error: {type(error).__name__}: {error}")
        msg = f"⚠️ An unexpected error occurred: `{type(error).__name__}`"

    if interaction.response.is_done():
        await interaction.followup.send(content=msg, ephemeral=True)
    else:
        await interaction.response.send_message(content=msg, ephemeral=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Loaded allowed user IDs: {ALLOWED_USER_IDS if ALLOWED_USER_IDS else 'All Users Allowed'}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} app commands.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


async def main():
    try:
        print(f"[*] Starting FB Report Bot...")
        await bot.start(BOT_TOKEN)

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Shutting down gracefully.")
    except Exception as e:
        print(f"\n[FATAL] {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)