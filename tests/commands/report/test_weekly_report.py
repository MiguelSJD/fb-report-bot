"""
Unit tests for weekly top 10 report generation logic.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from commands.report.weekly_report import generate_weekly_top_10_report
from utils.constants import DATE_FORMAT


def test_generate_weekly_top_10_report_sorting_and_screenshots():
    """Test top 10 items are correctly formatted as report cards with optional screenshots."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [
            today,
            "https://img.com/a.png",
            "Feature=Option A",
            "Obs A",
            "Cons A",
            "Sol A",
            "10",
        ],
        [today, "", "Feature=Option B", "Obs B", "Cons B", "Sol B", "500"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_weekly_top_10_report(mock_worksheet)

    assert len(messages) == 2
    assert "# **---  1. Topic: Feature  ---**" in messages[0]
    assert "Sum Votes = xxx" in messages[0]
    assert "- Option A" in messages[0]
    assert "**Screenshots:**\nhttps://img.com/a.png" in messages[0]

    assert "# **---  2. Topic: Feature  ---**" in messages[1]
    assert "Sum Votes = xxx" in messages[1]
    assert "- Option B" in messages[1]
    assert "**Screenshots:**" not in messages[1]


def test_generate_weekly_top_10_report_deduplication():
    """Edge Case: Test category/subcategory deduplication rule applies globally."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [today, "", "Store=Buy Crates", "Obs 1", "Cons 1", "Sol 1"],
        # Same Category & Subcategory -> Must be skipped globally
        [today, "", "Store=Buy Crates", "Obs 2", "Cons 2", "Sol 2"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_weekly_top_10_report(mock_worksheet)

    assert len(messages) == 1
    assert "Obs 1" in messages[0]
    assert "Obs 2" not in messages[0]


def test_generate_weekly_top_10_report_empty():
    """Test empty rows handling."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = []

    messages = generate_weekly_top_10_report(mock_worksheet)
    assert messages == ["No valid reports"]
