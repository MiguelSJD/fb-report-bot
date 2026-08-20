"""
Unit tests for mid-week report generation logic.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from commands.report.mid_week_report import generate_mid_week_report
from utils.constants import DATE_FORMAT


def test_generate_mid_week_report_detail_formatting():
    """Test summary header and topic card formatting via generate_mid_week_report."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [
            today,
            "https://screenshot.link/1.png",
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

    # Message 0: Summary header block
    # Message 1: First detailed topic card
    assert len(messages) == 2

    summary_msg = messages[0]
    assert "📈 Mid-Week Feedback Report" in summary_msg
    assert "### 📁 Performance (`100` total votes)" in summary_msg
    assert "• **FPS Drop** — `100` votes" in summary_msg

    card_msg = messages[1]
    assert "# **---  1. Topic: Performance  ---**" in card_msg
    assert "Sum Votes = 100" in card_msg
    assert "- FPS Drop" in card_msg
    assert "High GPU usage" in card_msg
    assert "Game freezes" in card_msg
    assert "Optimize shaders" in card_msg
    assert "**Screenshots:**\nhttps://screenshot.link/1.png" in card_msg


def test_generate_mid_week_report_deduplication_and_already_counted():
    """Test subcategory vote aggregation and total category vote calculation in summary."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        # Row 1: Subcategory "Bring back crates" (100 votes)
        [
            today,
            "https://link1.com",
            "Migo store = Bring back crates",
            "Obs 1",
            "Cons 1",
            "Sol 1",
            "100",
        ],
        # Row 2: Subcategory "Bring back crates" (50 votes)
        [
            today,
            "https://link2.com",
            "Migo store = Bring back crates",
            "Obs 2",
            "Cons 2",
            "Sol 2",
            "50",
        ],
        # Row 3: Subcategory "Remove bug items" (30 votes)
        [
            today,
            "https://link3.com",
            "Migo store = Remove bug items",
            "Obs 1",
            "Cons 1",
            "Sol 1",
            "30",
        ],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_mid_week_report(mock_worksheet)

    assert len(messages) == 2
    summary_msg = messages[0]
    card_msg = messages[1]

    # Total category votes: 100 + 50 + 30 = 180 total votes
    assert "### 📁 Migo store (`180` total votes)" in summary_msg
    assert "• **Bring back crates** — `100` votes" in summary_msg
    assert "• **Bring back crates** — `50` votes" in summary_msg
    assert "• **Remove bug items** — `30` votes" in summary_msg

    # Detailed card checks
    assert "- Bring back crates" in card_msg
    assert "- Remove bug items" in card_msg
    assert "https://link1.com" in card_msg
    assert "https://link2.com" not in card_msg
    assert "https://link3.com" in card_msg


def test_generate_mid_week_report_top_5_topic_limit():
    """Test top 5 topic limit ignores 6th new topic for detailed cards while generating summary."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        [today, "", "Top 1=Sub 1", "Obs 1", "Cons 1", "Sol 1", "10"],
        [today, "", "Top 2=Sub 2", "Obs 2", "Cons 2", "Sol 2", "10"],
        [today, "", "Top 3=Sub 3", "Obs 3", "Cons 3", "Sol 3", "10"],
        [today, "", "Top 4=Sub 4", "Obs 4", "Cons 4", "Sol 4", "10"],
        [today, "", "Top 5=Sub 5", "Obs 5", "Cons 5", "Sol 5", "10"],
        # 6th unique topic -> Skipped for detailed cards
        [today, "", "Top 6=Sub 6", "Obs 6", "Cons 6", "Sol 6", "10"],
        # Subcategory belonging to Top 1 -> Processed & added
        [today, "", "Top 1=Sub Extra", "Obs 1", "Cons 1", "Sol 1", "20"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_mid_week_report(mock_worksheet)

    # 1 Summary message + 5 detailed topic cards = 6 messages total
    assert len(messages) == 6

    summary_msg = messages[0]
    assert "📈 Mid-Week Feedback Report" in summary_msg

    top_1_card = messages[1]
    assert "Sum Votes = 30" in top_1_card
    assert "- Sub 1" in top_1_card
    assert "- Sub Extra" in top_1_card


def test_generate_mid_week_report_empty():
    """Test handling of completely empty worksheet rows."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = []

    messages = generate_mid_week_report(mock_worksheet)
    assert messages == ["No valid reports"]
