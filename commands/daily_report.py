"""
Daily report generator module for F&B Bot.
"""

import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone

import discord

from models.log_level import LogLevel
from utils.constants import DATE_FORMAT
from utils.discord import (
    handle_report_error,
    send_report_response,
    trigger_sheet_update,
)
from utils.formatting import (
    parse_topic_string,
    parse_vote_count,
)
from utils.google_sheets import get_report_worksheet
from utils.helper import extract_row_data
from utils.logger import log_event


@dataclass(frozen=True)
class DailyReportConfig:
    lookback_days_trigger: str = "1"
    start_row_idx: int = 3
    min_vote_threshold: int = 50


CONFIG = DailyReportConfig()


def generate_daily_report(worksheet) -> str:
    """Generate a daily report from the configured worksheet rows."""
    trigger_sheet_update(worksheet, CONFIG.lookback_days_trigger)

    all_values = worksheet.get_all_values()
    current_date = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    grouped_categories = OrderedDict()

    for row in all_values[CONFIG.start_row_idx :]:
        (
            row_date,
            _,
            topic_raw,
            _,
            _,
            _,
            votes_raw,
        ) = extract_row_data(row)

        if not row_date:
            break

        if row_date != current_date:
            continue

        vote_count = parse_vote_count(votes_raw)

        if vote_count < CONFIG.min_vote_threshold:
            continue

        category, subcategory = parse_topic_string(topic_raw)

        if category in grouped_categories:
            grouped_categories[category].append((subcategory, vote_count))
        else:
            if len(grouped_categories) >= 5:
                continue
            grouped_categories[category] = [(subcategory, vote_count)]

    header_block = f"# 📊 Daily Feedback Report\n**Date:** `{current_date}`\n\n---"

    if not grouped_categories:
        categories_block = "*No valid entries found meeting the criteria.*"
    else:
        category_sections = []
        for category, subcategories in grouped_categories.items():
            total_category_votes = sum(votes for _, votes in subcategories)
            subcategories_text = "\n".join(
                f"• **{sub}** — `{votes}` votes" for sub, votes in subcategories
            )
            category_sections.append(
                f"### 📁 {category} (`{total_category_votes}` total votes)\n"
                f"{subcategories_text}"
            )
        categories_block = "\n\n".join(category_sections)

    return f"{header_block}\n\n{categories_block}"


async def handle_daily_report(interaction: discord.Interaction):
    """Handle the daily-report slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

    try:
        log_event(
            guild_id, LogLevel.INFO, f"User {interaction.user} triggered /daily-report"
        )
        await interaction.response.defer(ephemeral=False)
        report_text = await asyncio.to_thread(
            lambda: generate_daily_report(get_report_worksheet())
        )
        await send_report_response(interaction, report_text)
    except (
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        await handle_report_error(
            interaction, exc, guild_id, "Daily report generation failed"
        )
