"""
Weekly Top 10 report generator module for FB Report Bot.
"""

import asyncio
from dataclasses import dataclass

import discord

from models.log_level import LogLevel
from utils.constants import (
    COL_CONSEQUENCE,
    COL_DATE,
    COL_OBSERVATION,
    COL_SCREENSHOT_LINK,
    COL_SOLUTION,
    COL_TOPIC,
)
from utils.discord import (
    handle_report_error,
    send_report_response,
    trigger_sheet_update,
)
from utils.formatting import (
    format_topic_report_card,
    get_clean_val,
    parse_topic_string,
    sanitize_markdown,
)
from utils.google_sheets import get_worksheet
from utils.logger import log_event


@dataclass(frozen=True)
class WeeklyTop10ReportConfig:
    lookback_days_trigger: str = "6"
    start_row_idx: int = 3


CONFIG = WeeklyTop10ReportConfig()


def generate_weekly_top_10_report(worksheet) -> list[str]:
    """Generate a weekly top 10 report from configured worksheet rows."""
    trigger_sheet_update(worksheet, CONFIG.lookback_days_trigger)

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
        screenshot_link = get_clean_val(all_values, row_idx, COL_SCREENSHOT_LINK)

        category, subcategory = parse_topic_string(topic_raw)

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

    return [
        format_topic_report_card(
            rank=rank,
            category=data["category"],
            votes_str="xxx",
            subcategories=data["subcategories"],
            observation=data["observation"],
            consequence=data["consequence"],
            solution=data["solution"],
            screenshots=data["screenshots"],
        )
        for rank, data in enumerate(topics_dict.values(), start=1)
    ]


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
        await handle_report_error(
            interaction, exc, guild_id, "Weekly report generation failed"
        )
