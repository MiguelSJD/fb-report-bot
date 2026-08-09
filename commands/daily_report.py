"""
Daily report generator module for FB Report Bot.
"""

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone

import discord
from gspread.exceptions import GSpreadException

from models.log_level import LogLevel
from utils.constants import (
    COL_DATE,
    COL_TOPIC,
    COL_VOTES,
    DATE_FORMAT,
    SHEET_UPDATE_DELAY,
    TRIGGER_CELL,
)
from utils.discord import send_report_response, validate_interaction
from utils.formatting import capitalize_text, get_clean_val
from utils.google_sheets import get_worksheet
from utils.logger import log_event


@dataclass(frozen=True)
class DailyReportConfig:
    lookback_days_trigger: str = "1"
    start_row_idx: int = 3
    end_row_idx: int = 8
    min_vote_threshold: int = 50
    topic_split_max: int = 1


CONFIG = DailyReportConfig()


def generate_daily_report(worksheet) -> str:
    """Generate a daily report from the configured worksheet rows."""
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
    current_date = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    grouped_categories = OrderedDict()
    data_issues = []
    all_rows_empty = True

    for row_idx in range(CONFIG.start_row_idx, CONFIG.end_row_idx):
        sheet_row_num = row_idx + 1
        row_date = get_clean_val(all_values, row_idx, COL_DATE)
        topic_raw = get_clean_val(all_values, row_idx, COL_TOPIC)
        votes_raw = get_clean_val(all_values, row_idx, COL_VOTES)

        is_empty_row = not row_date and not topic_raw and not votes_raw
        if is_empty_row:
            continue

        all_rows_empty = False

        if row_date != current_date:
            continue

        row_issues = []
        if not row_date:
            row_issues.append("missing date")
        if not topic_raw:
            row_issues.append("missing topic")
        elif "=" not in topic_raw:
            row_issues.append("missing '=' delimiter in topic")
        if not votes_raw:
            row_issues.append("missing vote count")

        vote_count = None
        if votes_raw:
            try:
                vote_count = int(votes_raw.replace(",", ""))
            except ValueError:
                row_issues.append(f"invalid vote format ('{votes_raw}')")

        if row_issues:
            data_issues.append(
                f"- **Row {sheet_row_num}**: Corrupted or incomplete data ({', '.join(row_issues)})."
            )
            continue

        if vote_count < CONFIG.min_vote_threshold:
            continue

        category_raw, subcategory_raw = topic_raw.split("=", CONFIG.topic_split_max)
        category = capitalize_text(category_raw)
        subcategory = capitalize_text(subcategory_raw)

        if category not in grouped_categories:
            grouped_categories[category] = []
        grouped_categories[category].append((subcategory, vote_count))

    if all_rows_empty:
        return "No valid reports"

    report_lines = [
        "# 📊 Daily Feedback Report",
        f"**Date:** `{current_date}`\n",
        "---",
    ]

    if not grouped_categories:
        report_lines.append("*No valid entries found meeting the criteria.*")
    else:
        for category, subcategories in grouped_categories.items():
            total_category_votes = sum(votes for _, votes in subcategories)
            report_lines.append(
                f"\n### 📁 {category} (`{total_category_votes}` total votes)"
            )
            for subcategory, votes in subcategories:
                report_lines.append(f"• **{subcategory}** — `{votes}` votes")

    if data_issues:
        report_lines.append("\n---")
        report_lines.append("### ⚠️ Observations")
        report_lines.extend(data_issues)

    return "\n".join(report_lines)


async def handle_daily_report(interaction: discord.Interaction):
    """Handle the daily-report slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None
    is_valid, error_msg = validate_interaction(interaction)
    if not is_valid:
        log_event(
            guild_id, LogLevel.WARNING, f"Invalid daily-report interaction: {error_msg}"
        )
        await interaction.response.send_message(content=error_msg, ephemeral=True)
        return

    try:
        log_event(
            guild_id, LogLevel.INFO, f"User {interaction.user} triggered /daily-report"
        )
        await interaction.response.defer(ephemeral=False)
        report_text = await asyncio.to_thread(
            lambda: generate_daily_report(get_worksheet())
        )
        await send_report_response(interaction, report_text)
    except (
        discord.HTTPException,
        discord.app_commands.AppCommandError,
        discord.DiscordException,
    ) as exc:
        log_event(
            guild_id, LogLevel.ERROR, f"Daily report generation failed: {exc}", exc=exc
        )
        error_msg = f"❌ **Report generation failed**\n\n`{exc!s}`"
        await interaction.followup.send(content=error_msg, ephemeral=True)
