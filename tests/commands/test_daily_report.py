"""
Unit tests for daily report generation logic.
"""

from unittest.mock import MagicMock
from datetime import datetime
from commands.daily_report import generate_daily_report
from utils.constants import DATE_FORMAT


def test_generate_daily_report_valid_data():
    """Test generating a report with valid current date data."""
    today = datetime.now().strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [today, "", "Bug=FPS Drop", "", "", "", "150"],
        [today, "", "UI=Missing Button", "", "", "", "20"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    report = generate_daily_report(mock_worksheet)

    assert "# 📊 Daily Feedback Report" in report
    assert "### 📁 Bug (`150` total votes)" in report
    assert "• **FPS Drop** — `150` votes" in report
    assert "Missing Button" not in report


def test_generate_daily_report_corrupted_data():
    """Test handling of rows with missing fields or invalid vote formats."""
    today = datetime.now().strftime(DATE_FORMAT)

    mock_values = [
        [], [], [],
        [today, "", "InvalidTopicNoDelimiter", "", "", "", "100"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    report = generate_daily_report(mock_worksheet)

    assert "### ⚠️ Observations" in report
    assert "Corrupted or incomplete data" in report
    assert "missing '=' delimiter in topic" in report
