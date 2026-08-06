"""
Weekly Top 10 report generator module for FB Report Bot.
"""

import time
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

LOOKBACK_DAYS_VALUE = "6"
START_ROW_IDX = 3
END_ROW_IDX = 13


def generate_weekly_top_10_report(worksheet) -> list[str]:
    """Generate a weekly top 10 report from rows 4-13 of the worksheet."""
    try:
        worksheet.update_acell(TRIGGER_CELL, LOOKBACK_DAYS_VALUE)
        time.sleep(SHEET_UPDATE_DELAY)
    except Exception as exc:
        print(f"Warning: Failed to update cell {TRIGGER_CELL}: {exc}")

    all_values = worksheet.get_all_values()
    report_items = []
    all_rows_empty = True

    for row_idx in range(START_ROW_IDX, END_ROW_IDX):
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

        topic_parts = topic_raw.split("=", 1)
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
    for rank, item in enumerate(report_items, start=1):
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