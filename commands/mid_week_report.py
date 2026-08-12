"""
Mid-week report generator module for FB Report Bot.
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
    COL_VOTES,
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
    parse_vote_count,
    sanitize_markdown,
)
from utils.google_sheets import get_worksheet
from utils.logger import log_event


@dataclass(frozen=True)
class MidWeekReportConfig:
    lookback_days_trigger: str = "2"
    start_row_idx: int = 3


CONFIG = MidWeekReportConfig()


def generate_mid_week_report(worksheet) -> list[str]:
    """Generate a mid-week report spanning configured lookback days prior up to current day."""
    trigger_sheet_update(worksheet, CONFIG.lookback_days_trigger)

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
        screenshot_link = get_clean_val(all_values, row_idx, COL_SCREENSHOT_LINK)

        vote_count = parse_vote_count(votes_raw)
        category, subcategory = parse_topic_string(topic_raw)

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

    return [
        format_topic_report_card(
            rank=rank,
            category=data["category"],
            votes_str=str(data["votes"]),
            subcategories=data["subcategories"],
            observation=data["observation"],
            consequence=data["consequence"],
            solution=data["solution"],
            screenshots=data["screenshots"],
        )
        for rank, data in enumerate(topics_dict.values(), start=1)
    ]


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
        await handle_report_error(
            interaction, exc, guild_id, "Mid-week report generation failed"
        )
