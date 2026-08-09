"""
Unit tests for mid-week report generation logic.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from commands.mid_week_report import generate_mid_week_report
from utils.constants import DATE_FORMAT


def test_generate_mid_week_report_detail_formatting():
    """Test category detail message formatting via the public generate_mid_week_report interface."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [
            today,
            "",
            "Performance=FPS Drop",
            "High GPU usage",
            "Game freezes",
            "Optimize shaders",
            "100",
        ],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_mid_week_report(mock_worksheet)

    assert len(messages) == 2
    detail_msg = messages[1]

    assert "**1. Performance**" in detail_msg
    assert "- FPS Drop (100 votes)" in detail_msg
    assert "Total votes (100 votes)" in detail_msg
    assert "- High GPU usage" in detail_msg
    assert "- Game freezes" in detail_msg
    assert "- Optimize shaders" in detail_msg


def test_generate_mid_week_report_valid_data():
    """Test generating mid-week summary and detail messages."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [
            today,
            "",
            "Bug=Lag Spike",
            "Server overload",
            "DC users",
            "Upgrade server",
            "200",
        ],
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
