"""
Weekly Top 10 report generator module for FB Report Bot.
"""

import time
import asyncio
import discord
from dataclasses import dataclass

from utils.constants import (
    TRIGGER_CELL,
    SHEET_UPDATE_DELAY,
    COL_DATE,
    COL_TOPIC,
    COL_OBSERVATION,
    COL_CONSEQUENCE,
    COL_SOLUTION,
    COL_VOTES,
)
from utils.formatting import get_clean_val, capitalize_text, sanitize_markdown
from utils.google_sheets import get_worksheet
from utils.discord import send_report_response, validate_interaction
from models.log_level import LogLevel
from utils.logger import log_event


@dataclass(frozen=True)
class WeeklyTop10ReportConfig:
    lookback_days_trigger: str = "6"
    start_row_idx: int = 3
    end_row_idx: int = 13
    topic_split_max: int = 1
    rank_start_index: int = 1


CONFIG = WeeklyTop10ReportConfig()


def generate_weekly_top_10_report(worksheet) -> list[str]:
    """Generate a weekly top 10 report from configured worksheet rows."""
    try:
        worksheet.update_acell(TRIGGER_CELL, CONFIG.lookback_days_trigger)
        time.sleep(SHEET_UPDATE_DELAY)
    except Exception as exc:
        log_event(None, LogLevel.WARNING, f"Failed to update trigger cell {TRIGGER_CELL}: {exc}", exc=exc)

    all_values = worksheet.get_all_values()
    report_items = []
    all_rows_empty = True

    for row_idx in range(CONFIG.start_row_idx, CONFIG.end_row_idx):
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
            continue

        topic_parts = topic_raw.split("=", CONFIG.topic_split_max)
        category = capitalize_text(topic_parts[0])
        subcategory = capitalize_text(topic_parts[1])

        report_items.append({
            "category": category,
            "subcategory": subcategory,
            "votes": vote_count,
            "observation": sanitize_markdown(observation),
            "consequence": sanitize_markdown(consequence),
            "solution": sanitize_markdown(solution),
        })

    if all_rows_empty or not report_items:
        return ["No valid reports"]

    report_items.sort(key=lambda item: item["votes"], reverse=True)

    messages = []
    for rank, item in enumerate(report_items, start=CONFIG.rank_start_index):
        message_content = (
            f"**--- {rank}. Topic: {item['category']} ---**\n"
            f"Sum Votes = {item['votes']}\n\n"
            f"**Description:**\n"
            f"{item['subcategory']}\n\n"
            f"**Observation:**\n"
            f"{item['observation']}\n\n"
            f"**Consequence:**\n"
            f"{item['consequence']}\n\n"
            f"**Suggested Solution:**\n"
            f"{item['solution']}\n\n"
            f"**State:**\n"
            f"All"
        )
        messages.append(message_content)

    return messages


async def handle_weekly_report_top_10(interaction: discord.Interaction):
    """Handle the weekly-report-top-10 slash command logic."""
    guild_id = interaction.guild_id if interaction.guild else None
    is_valid, error_msg = validate_interaction(interaction)
    if not is_valid:
        log_event(guild_id, LogLevel.WARNING, f"Invalid weekly-report interaction: {error_msg}")
        await interaction.response.send_message(content=error_msg, ephemeral=True)
        return

    try:
        log_event(guild_id, LogLevel.INFO, f"User {interaction.user} triggered /weekly-report-top-10")
        await interaction.response.defer(ephemeral=False)
        report_messages = await asyncio.to_thread(lambda: generate_weekly_top_10_report(get_worksheet()))
        await send_report_response(interaction, report_messages)
    except Exception as e:
        log_event(guild_id, LogLevel.ERROR, f"Weekly report generation failed: {e}", exc=e)
        error_msg = f"❌ **Report generation failed**\n\n`{str(e)}`"
        if interaction.response.is_done():
            await interaction.followup.send(content=error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(content=error_msg, ephemeral=True)