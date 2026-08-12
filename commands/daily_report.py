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
from utils.discord import send_report_response
from utils.formatting import capitalize_text, get_clean_val
from utils.google_sheets import get_worksheet
from utils.logger import log_event


@dataclass(frozen=True)
class DailyReportConfig:
    lookback_days_trigger: str = "1"
    start_row_idx: int = 3
    min_vote_threshold: int = 50


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
    row_idx = CONFIG.start_row_idx

    while True:
        sheet_row_num = row_idx + 1
        row_date = get_clean_val(all_values, row_idx, COL_DATE)

        if not row_date:
            break

        topic_raw = get_clean_val(all_values, row_idx, COL_TOPIC)
        votes_raw = get_clean_val(all_values, row_idx, COL_VOTES)

        all_rows_empty = False

        if row_date != current_date:
            row_idx += 1
            continue

        row_issues = []
        if not topic_raw:
            row_issues.append("missing topic")
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
            row_idx += 1
            continue

        if vote_count < CONFIG.min_vote_threshold:
            row_idx += 1
            continue

        category_raw, _, subcategory_raw = topic_raw.partition("=")
        category = capitalize_text(category_raw)
        subcategory = capitalize_text(subcategory_raw)

        if category in grouped_categories:
            grouped_categories[category].append((subcategory, vote_count))
        else:
            if len(grouped_categories) >= 5:
                row_idx += 1
                continue
            grouped_categories[category] = [(subcategory, vote_count)]

        row_idx += 1

    if all_rows_empty:
        return "No valid reports"

    header_block = (
        f"# 📊 Daily Feedback Report\n"
        f"**Date:** `{current_date}`\n\n"
        f"---"
    )

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

    observations_block = ""
    if data_issues:
        issues_text = "\n".join(data_issues)
        observations_block = f"\n\n---\n### ⚠️ Observations\n{issues_text}"

    report_text = f"{header_block}\n\n{categories_block}{observations_block}"

    return report_text


async def handle_daily_report(interaction: discord.Interaction):
    """Handle the daily-report slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None

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