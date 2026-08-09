"""
Mid-week report generator module for FB Report Bot.
"""

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import discord
from gspread.exceptions import GSpreadException

from models.log_level import LogLevel
from utils.constants import (
    COL_CONSEQUENCE,
    COL_DATE,
    COL_OBSERVATION,
    COL_SOLUTION,
    COL_TOPIC,
    COL_VOTES,
    DATE_FORMAT,
    SHEET_UPDATE_DELAY,
    TRIGGER_CELL,
)
from utils.discord import send_report_response, validate_interaction
from utils.formatting import (
    capitalize_text,
    get_clean_val,
    get_unique_non_empty,
    sanitize_markdown,
)
from utils.google_sheets import get_worksheet
from utils.logger import log_event


@dataclass(frozen=True)
class MidWeekReportConfig:
    lookback_days_trigger: str = "2"
    lookback_days_delta: int = 2
    start_row_idx: int = 3
    end_row_idx: int = 8
    topic_split_max: int = 1
    rank_start_index: int = 1


CONFIG = MidWeekReportConfig()


def _build_category_detail_message(
    position: int, category: str, items: list[dict]
) -> str:
    """Formats a single category's detailed feedback into a formatted report block."""
    total_category_votes = sum(item["votes"] for item in items)
    lines = [f"—-———-—- **{position}. {category}** ———————--"]

    for item in items:
        lines.append(f"- {item['subcategory']} ({item['votes']} votes)")

    lines.append(f"\nTotal votes ({total_category_votes} votes)\n")

    lines.append("**Observation:**")
    for obs in get_unique_non_empty(items, "observation"):
        lines.append(f"- {obs}")
    lines.append("")

    lines.append("**Consequences:**")
    for cons in get_unique_non_empty(items, "consequence"):
        lines.append(f"- {cons}")
    lines.append("")

    lines.append("**Suggested Solutions:**")
    for sol in get_unique_non_empty(items, "solution"):
        lines.append(f"- {sol}")

    return "\n".join(lines)


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

    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=CONFIG.lookback_days_delta)).strftime(
        DATE_FORMAT
    )
    end_date = now.strftime(DATE_FORMAT)

    grouped_categories = OrderedDict()
    data_issues = []
    all_rows_empty = True

    for row_idx in range(CONFIG.start_row_idx, CONFIG.end_row_idx):
        sheet_row_num = row_idx + 1
        date_val = get_clean_val(all_values, row_idx, COL_DATE)
        topic_raw = get_clean_val(all_values, row_idx, COL_TOPIC)
        observation = get_clean_val(all_values, row_idx, COL_OBSERVATION)
        consequence = get_clean_val(all_values, row_idx, COL_CONSEQUENCE)
        solution = get_clean_val(all_values, row_idx, COL_SOLUTION)
        votes_raw = get_clean_val(all_values, row_idx, COL_VOTES)

        is_empty_row = not date_val and not topic_raw and not votes_raw
        if is_empty_row:
            continue

        all_rows_empty = False

        row_issues = []
        if not date_val:
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

        topic_parts = topic_raw.split("=", CONFIG.topic_split_max)
        category = capitalize_text(topic_parts[0])
        subcategory = capitalize_text(topic_parts[1])

        if category not in grouped_categories:
            grouped_categories[category] = []

        grouped_categories[category].append(
            {
                "subcategory": sanitize_markdown(subcategory),
                "votes": vote_count,
                "observation": sanitize_markdown(observation),
                "consequence": sanitize_markdown(consequence),
                "solution": sanitize_markdown(solution),
            }
        )

    if all_rows_empty:
        return ["No valid reports"]

    summary_lines = [
        "# 📈 Mid-Week Feedback Report",
        f"**Period:** `{start_date}` to `{end_date}`\n",
        "---",
    ]

    if not grouped_categories:
        summary_lines.append("*No valid entries found.*")
    else:
        for category, items in grouped_categories.items():
            total_category_votes = sum(item["votes"] for item in items)
            summary_lines.append(
                f"\n### 📁 {category} (`{total_category_votes}` total votes)"
            )
            for item in items:
                summary_lines.append(
                    f"• **{item['subcategory']}** — `{item['votes']}` votes"
                )

    if data_issues:
        summary_lines.append("\n---")
        summary_lines.append("### ⚠️ Observations")
        summary_lines.extend(data_issues)

    messages = ["\n".join(summary_lines)]

    if not grouped_categories:
        return messages

    sorted_categories = sorted(
        grouped_categories.items(),
        key=lambda entry: sum(item["votes"] for item in entry[1]),
        reverse=True,
    )

    for position, (category, items) in enumerate(
        sorted_categories, start=CONFIG.rank_start_index
    ):
        message = _build_category_detail_message(position, category, items)
        messages.append(message)

    return messages


async def handle_mid_week_report(interaction: discord.Interaction):
    """Handle the mid-week-report slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None
    is_valid, error_msg = validate_interaction(interaction)
    if not is_valid:
        log_event(
            guild_id,
            LogLevel.WARNING,
            f"Invalid mid-week-report interaction: {error_msg}",
        )
        await interaction.response.send_message(content=error_msg, ephemeral=True)
        return

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
