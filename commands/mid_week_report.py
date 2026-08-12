"""
Mid-week report generator module for FB Report Bot.
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
    COL_VOTES,
    SHEET_UPDATE_DELAY,
    TRIGGER_CELL,
)
from utils.discord import send_report_response
from utils.formatting import capitalize_text, get_clean_val, sanitize_markdown
from utils.google_sheets import get_worksheet
from utils.logger import log_event


@dataclass(frozen=True)
class MidWeekReportConfig:
    lookback_days_trigger: str = "2"
    start_row_idx: int = 3


CONFIG = MidWeekReportConfig()


def generate_mid_week_report(worksheet) -> list[str]:
    """Generate a mid-week report spanning configured lookback days prior up to current day."""
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
    seen_category_subcats = set()
    row_idx = CONFIG.start_row_idx

    while True:
        date_val = get_clean_val(all_values, row_idx, COL_DATE)

        if not date_val:
            break

        topic_raw = get_clean_val(all_values, row_idx, COL_TOPIC)
        observation = get_clean_val(all_values, row_idx, COL_OBSERVATION)
        consequence = get_clean_val(all_values, row_idx, COL_CONSEQUENCE)
        solution = get_clean_val(all_values, row_idx, COL_SOLUTION)
        votes_raw = get_clean_val(all_values, row_idx, COL_VOTES)
        screenshot_link = get_clean_val(all_values, row_idx, COL_SCREEN_SHOT_LINK)

        vote_count = 0
        if votes_raw:
            try:
                vote_count = int(votes_raw.replace(",", ""))
            except ValueError:
                vote_count = 0

        category_raw, _, subcategory_raw = topic_raw.partition("=")
        category = capitalize_text(category_raw)
        subcategory = capitalize_text(subcategory_raw)

        if (category, subcategory) in seen_category_subcats:
            row_idx += 1
            continue

        seen_category_subcats.add((category, subcategory))

        obs_sanitized = sanitize_markdown(observation)
        topic_key = (category, obs_sanitized)

        if topic_key in topics_dict:
            if subcategory:
                topics_dict[topic_key]["subcategories"].append(subcategory)
            if screenshot_link:
                topics_dict[topic_key]["screenshots"].append(screenshot_link)
            topics_dict[topic_key]["votes"] += vote_count

        else:
            if len(topics_dict) >= 5:
                row_idx += 1
                continue

            topics_dict[topic_key] = {
                "category": category,
                "subcategories": [subcategory] if subcategory else [],
                "observation": obs_sanitized,
                "consequence": sanitize_markdown(consequence),
                "solution": sanitize_markdown(solution),
                "votes": vote_count,
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
            f"Sum Votes = {data['votes']}\n\n"
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


async def handle_mid_week_report(interaction: discord.Interaction):
    """Handle the mid-week-report slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        log_event(
            guild_id,
            LogLevel.INFO,
            f"User {interaction.user} triggered /mid-week-report",
        )
        await interaction.response.defer(ephemeral=False)
        report_messages = await asyncio.to_thread(
            lambda: generate_mid_week_report(get_worksheet())
        )
        await send_report_response(interaction, report_messages)
    except (
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id,
            LogLevel.ERROR,
            f"Mid-week report generation failed: {exc}",
            exc=exc,
        )
        error_msg = f"❌ **Report generation failed**\n\n`{exc!s}`"
        if interaction.response.is_done():
            await interaction.followup.send(content=error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(content=error_msg, ephemeral=True)