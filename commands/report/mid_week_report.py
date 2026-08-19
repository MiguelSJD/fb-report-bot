"""
Mid-week report generator module for F&B Bot.
"""

import asyncio
from dataclasses import dataclass

import discord

from models.log_level import LogLevel
from utils.discord import (
    handle_report_error,
    send_report_response,
    trigger_sheet_update,
)
from utils.formatting import (
    format_topic_report_card,
    parse_topic_string,
    parse_vote_count,
    sanitize_markdown,
)
from utils.google_sheets import get_report_worksheet
from utils.logger import log_event
from utils.report_helper import extract_row_data


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

    for row in all_values[CONFIG.start_row_idx :]:
        (
            date_val,
            screenshot_link,
            topic_raw,
            observation,
            consequence,
            solution,
            votes_raw,
        ) = extract_row_data(row)

        if not date_val:
            break

        vote_count = parse_vote_count(votes_raw)
        category, subcategory = parse_topic_string(topic_raw)

        if (category, subcategory) in seen_category_subcats:
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
            lambda: generate_mid_week_report(get_report_worksheet())
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
