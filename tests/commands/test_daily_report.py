"""
Unit tests for daily report generation logic.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from commands.daily_report import generate_daily_report
from utils.constants import DATE_FORMAT


def test_generate_daily_report_valid_data():
    """Test generating a report with valid current date data."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

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
    assert "Missing Button" not in report  # Filtered out due to min_vote_threshold (20 < 50)


def test_generate_daily_report_corrupted_data():
    """Test handling of rows with missing fields or invalid vote formats."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [today, "", "", "", "", "", "100"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    report = generate_daily_report(mock_worksheet)

    assert "### ⚠️ Observations" in report
    assert "Corrupted or incomplete data" in report
    assert "missing topic" in report


def test_generate_daily_report_top_5_overflow_and_topic_whitespace():
    """Edge Case: Test 5-category limit skipping 6th category, trimming spaces, and parsing topics without '='."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [today, "", "Cat 1 = Sub 1", "", "", "", "100"],
        [today, "", "Cat 2 = Sub 2", "", "", "", "100"],
        [today, "", "Cat 3 = Sub 3", "", "", "", "100"],
        [today, "", "Cat 4 = Sub 4", "", "", "", "100"],
        [today, "", "Cat 5 = Sub 5", "", "", "", "100"],
        # 6th unique category -> Should be ignored
        [today, "", "Cat 6 = Sub 6", "", "", "", "100"],
        # Subcategory belonging to an existing category (Cat 1) -> Should be appended
        [today, "", " Cat 1  =  Extra Sub ", "", "", "", "200"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    report = generate_daily_report(mock_worksheet)

    assert "Cat 1" in report
    assert "Cat 5" in report
    assert "Cat 6" not in report  # 6th category skipped
    assert "Extra Sub" in report  # Belonged to Cat 1 so it was collected
    assert "### 📁 Cat 1 (`300` total votes)" in report  # 100 + 200 votes