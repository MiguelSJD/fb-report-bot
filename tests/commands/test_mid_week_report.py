"""
Unit tests for mid-week report generation logic.
"""

from unittest.mock import MagicMock
from datetime import datetime, timedelta
from commands.mid_week_report import generate_mid_week_report, _build_category_detail_message
from utils.constants import DATE_FORMAT


def test_build_category_detail_message():
    """Test formatting of detailed category blocks."""
    items = [
        {
            "subcategory": "FPS Drop",
            "votes": 100,
            "observation": "High GPU usage",
            "consequence": "Game freezes",
            "solution": "Optimize shaders",
        }
    ]
    message = _build_category_detail_message(1, "Performance", items)

    assert "**1. Performance**" in message
    assert "- FPS Drop (100 votes)" in message
    assert "Total votes (100 votes)" in message
    assert "- High GPU usage" in message
    assert "- Game freezes" in message
    assert "- Optimize shaders" in message


def test_generate_mid_week_report_valid_data():
    """Test generating mid-week summary and detail messages."""
    today = datetime.now().strftime(DATE_FORMAT)

    mock_values = [
        [], [], [],
        [today, "", "Bug=Lag Spike", "Server overload", "DC users", "Upgrade server", "200"],
        [today, "", "UI=Overlap", "Bad scaling", "Unreadable text", "Fix CSS", "50"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_mid_week_report(mock_worksheet)

    assert len(messages) == 3
    assert "# 📈 Mid-Week Feedback Report" in messages[0]
    assert "### 📁 Bug (`200` total votes)" in messages[0]
    assert "Bug" in messages[1]
    assert "UI" in messages[2]


def test_generate_mid_week_report_empty():
    """Test handling of completely empty worksheet rows."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = []

    messages = generate_mid_week_report(mock_worksheet)
    assert messages == ["No valid reports"]
