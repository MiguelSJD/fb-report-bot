"""
Weekly Top 10 report generator module for FB Report Bot.
"""

import asyncio
import time
from dataclasses import dataclass

import discord
from gspread.exceptions import GSpreadException

from models.log_level import LogLevel
from utils.constants import (
    COL_CONSEQUENCE,
    COL_DATE,
    COL_OBSERVATION,
    COL_SCREEN_SHOT_LINK,
    COL_SOLUTION,
    COL_TOPIC,
    SHEET_UPDATE_DELAY,
    TRIGGER_CELL,
)
from utils.discord import send_report_response
from utils.formatting import capitalize_text, get_clean_val, sanitize_markdown
from utils.google_sheets import get_worksheet
from utils.logger import log_event


@dataclass(frozen=True)
class WeeklyTop10ReportConfig:
    lookback_days_trigger: str = "6"
    start_row_idx: int = 3


CONFIG = WeeklyTop10ReportConfig()


def generate_weekly_top_10_report(worksheet) -> list[str]:
    """Generate a weekly top 10 report from configured worksheet rows."""
    try:
        worksheet.update_acell(TRIGGER_CELL, CONFIG.lookback_days_trigger)
        time.sleep(SHEET_UPDATE_DELAY)
    except GSpreadException as exc:
        log_event(
            None,
            LogLevel.WARNING,
            f"Failed to update trigger cell {TRIGGER_CELL}: {exc}",
            exc=exc,
        )

    all_values = worksheet.get_all_values()

    topics_dict = {}
    seen_category_subcategories = set()
    row_idx = CONFIG.start_row_idx

    while True:
        date_val = get_clean_val(all_values, row_idx, COL_DATE)

        if not date_val:
            break

        topic_raw = get_clean_val(all_values, row_idx, COL_TOPIC)
        observation = get_clean_val(all_values, row_idx, COL_OBSERVATION)
        consequence = get_clean_val(all_values, row_idx, COL_CONSEQUENCE)
        solution = get_clean_val(all_values, row_idx, COL_SOLUTION)
        screenshot_link = get_clean_val(all_values, row_idx, COL_SCREEN_SHOT_LINK)

        category_raw, _, subcategory_raw = topic_raw.partition("=")
        category = capitalize_text(category_raw)
        subcategory = capitalize_text(subcategory_raw)

        if (category, subcategory) in seen_category_subcategories:
            row_idx += 1
            continue

        seen_category_subcategories.add((category, subcategory))

        obs_sanitized = sanitize_markdown(observation)
        topic_key = (category, obs_sanitized)

        if topic_key in topics_dict:
            if subcategory:
                topics_dict[topic_key]["subcategories"].append(subcategory)
            if screenshot_link:
                topics_dict[topic_key]["screenshots"].append(screenshot_link)
        else:
            if len(topics_dict) >= 10:
                break

            topics_dict[topic_key] = {
                "category": category,
                "subcategories": [subcategory] if subcategory else [],
                "observation": obs_sanitized,
                "consequence": sanitize_markdown(consequence),
                "solution": sanitize_markdown(solution),
                "screenshots": [screenshot_link] if screenshot_link else [],
            }

        row_idx += 1

    if not topics_dict:
        return ["No valid reports"]

    messages = []
    for rank, data in enumerate(topics_dict.values(), start=1):
        subcategories_text = "\n".join(
            f"- {sub}" for sub in data["subcategories"] if sub
        )
        desc_block = (
            f"**Description:**\n{subcategories_text}\n"
            if subcategories_text
            else "**Description:**\n"
        )

        message_content = (
            f"# **---  {rank}. Topic: {data['category']}  ---**\n"
            f"Sum Votes = xxx\n\n"
            f"{desc_block}\n"
            f"**Observation:**\n"
            f"{data['observation']}\n\n"
            f"**Consequence:**\n"
            f"{data['consequence']}\n\n"
            f"**Suggested Solution:**\n"
            f"{data['solution']}"
        )

        if data["screenshots"]:
            screenshots_text = "\n".join(data["screenshots"])
            message_content += f"\n\n**Screenshots:**\n{screenshots_text}"

        messages.append(message_content)

    return messages


async def handle_weekly_report_top_10(interaction: discord.Interaction):
    """Handle the weekly-report-top-10 slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        log_event(
            guild_id,
            LogLevel.INFO,
            f"User {interaction.user} triggered /weekly-report-top-10",
        )
        await interaction.response.defer(ephemeral=False)
        report_messages = await asyncio.to_thread(
            lambda: generate_weekly_top_10_report(get_worksheet())
        )
        await send_report_response(interaction, report_messages)
    except (
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Weekly report generation failed: {exc}", exc=exc
        )
        error_msg = f"❌ **Report generation failed**\n\n`{exc!s}`"
        if interaction.response.is_done():
            await interaction.followup.send(content=error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(content=error_msg, ephemeral=True)