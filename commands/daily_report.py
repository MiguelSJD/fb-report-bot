"""
Daily report generator module for FB Report Bot.
"""

import time
from collections import OrderedDict
from datetime import datetime
from utils.constants import (
    TRIGGER_CELL,
    SHEET_UPDATE_DELAY,
    COL_DATE,
    COL_TOPIC,
    COL_VOTES,
)
from utils.formatting import get_clean_val, capitalize_text

LOOKBACK_DAYS_VALUE = "1"
START_ROW_IDX = 3
END_ROW_IDX = 8
MIN_VOTE_THRESHOLD = 50


def generate_daily_report(worksheet) -> str:
    """Generate a daily report from rows 4-8 of the worksheet."""
    try:
        worksheet.update_acell(TRIGGER_CELL, LOOKBACK_DAYS_VALUE)
        time.sleep(SHEET_UPDATE_DELAY)
    except Exception as exc:
        print(f"Warning: Failed to update cell {TRIGGER_CELL}: {exc}")

    all_values = worksheet.get_all_values()
    current_date = datetime.now().strftime("%d/%m/%Y")

    grouped_categories = OrderedDict()
    data_issues = []
    all_rows_empty = True

    for row_idx in range(START_ROW_IDX, END_ROW_IDX):
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
            data_issues.append(f"- **Row {sheet_row_num}**: Corrupted or incomplete data ({', '.join(row_issues)}).")
            continue

        if vote_count < MIN_VOTE_THRESHOLD:
            continue

        topic_parts = topic_raw.split("=", 1)
        category = capitalize_text(topic_parts[0])
        subcategory = capitalize_text(topic_parts[1])

        if category not in grouped_categories:
            grouped_categories[category] = []
        grouped_categories[category].append((subcategory, vote_count))

    if all_rows_empty:
        return "No valid reports"

    report_lines = ["# 📊 Daily Feedback Report", f"**Date:** `{current_date}`\n", "---"]

    if not grouped_categories:
        report_lines.append("*No valid entries found meeting the criteria.*")
    else:
        for category, subcategories in grouped_categories.items():
            total_category_votes = sum(votes for _, votes in subcategories)
            report_lines.append(f"\n### 📁 {category} (`{total_category_votes}` total votes)")
            for subcategory, votes in subcategories:
                report_lines.append(f"• **{subcategory}** — `{votes}` votes")

    if data_issues:
        report_lines.append("\n---")
        report_lines.append("### ⚠️ Observations")
        report_lines.extend(data_issues)

    return "\n".join(report_lines)