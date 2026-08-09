"""
Unit tests for weekly top 10 report generation logic.
"""

from unittest.mock import MagicMock
from datetime import datetime
from commands.weekly_report import generate_weekly_top_10_report
from utils.constants import DATE_FORMAT


def test_generate_weekly_top_10_report_sorting():
    """Test top 10 items are correctly sorted by vote count descending."""
    today = datetime.now().strftime(DATE_FORMAT)

    mock_values = [
        [], [], [],
        [today, "", "Feature=Option A", "Obs A", "Cons A", "Sol A", "10"],
        [today, "", "Feature=Option B", "Obs B", "Cons B", "Sol B", "500"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_weekly_top_10_report(mock_worksheet)

    assert len(messages) == 2
    assert "**--- 1. Topic: Feature ---**" in messages[0]
    assert "Sum Votes = 500" in messages[0]
    assert "Option B" in messages[0]

    assert "**--- 2. Topic: Feature ---**" in messages[1]
    assert "Sum Votes = 10" in messages[1]


def test_generate_weekly_top_10_report_empty():
    """Test empty rows handling."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = []

    messages = generate_weekly_top_10_report(mock_worksheet)
    assert messages == ["No valid reports"]