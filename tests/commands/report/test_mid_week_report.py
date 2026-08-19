"""
Unit tests for mid-week report generation logic.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from commands.report.mid_week_report import generate_mid_week_report
from utils.constants import DATE_FORMAT


def test_generate_mid_week_report_detail_formatting():
    """Test topic card formatting via the public generate_mid_week_report interface."""
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

    assert len(messages) == 1
    card_msg = messages[0]

    assert "# **---  1. Topic: Performance  ---**" in card_msg
    assert "Sum Votes = 100" in card_msg
    assert "- FPS Drop" in card_msg
    assert "High GPU usage" in card_msg
    assert "Game freezes" in card_msg
    assert "Optimize shaders" in card_msg
    assert "**Screenshots:**\nhttps://screenshot.link/1.png" in card_msg


def test_generate_mid_week_report_deduplication_and_screenshots():
    """Edge Case: Test strict category/subcategory deduplication and combining multiple screenshots."""
    today = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    mock_values = [
        [],
        [],
        [],
        # Row 1: Migo Store = Crates
        [
            today,
            "https://link1.com",
            "Migo store = Bring back crates",
            "Obs 1",
            "Cons 1",
            "Sol 1",
            "50",
        ],
        # Row 2: Same Category & Subcategory, different observation -> MUST BE SKIPPED GLOBALLY
        [
            today,
            "https://link2.com",
            "Migo store = Bring back crates",
            "Obs 2",
            "Cons 2",
            "Sol 2",
            "50",
        ],
        # Row 3: Same Topic (Category + Obs 1), new Subcategory -> MUST BE AGGREGATED
        [
            today,
            "https://link3.com",
            "Migo store = Remove bug items",
            "Obs 1",
            "Cons 1",
            "Sol 1",
            "100",
        ],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_mid_week_report(mock_worksheet)

    assert len(messages) == 1
    card_msg = messages[0]

    # Row 1 (50 votes) + Row 3 (100 votes) = 150 votes (Row 2 was skipped as duplicate subcategory)
    assert "Sum Votes = 150" in card_msg
    assert "- Bring back crates" in card_msg
    assert "- Remove bug items" in card_msg
    # Link 1 and Link 3 included; Link 2 skipped
    assert "https://link1.com" in card_msg
    assert "https://link2.com" not in card_msg
    assert "https://link3.com" in card_msg


def test_generate_mid_week_report_top_5_topic_limit():
    """Edge Case: Test top 5 topic limit ignores 6th new topic but continues parsing for top 5."""
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
        # 6th unique (category, observation) topic -> Skipped
        [today, "", "Top 6=Sub 6", "Obs 6", "Cons 6", "Sol 6", "10"],
        # Subcategory belonging to Top 1 -> Processed & added
        [today, "", "Top 1=Sub Extra", "Obs 1", "Cons 1", "Sol 1", "20"],
    ]

    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = mock_values

    messages = generate_mid_week_report(mock_worksheet)

    assert len(messages) == 5
    top_1_card = messages[0]
    assert "Sum Votes = 30" in top_1_card  # 10 + 20
    assert "- Sub 1" in top_1_card
    assert "- Sub Extra" in top_1_card


def test_generate_mid_week_report_empty():
    """Test handling of completely empty worksheet rows."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = []

    messages = generate_mid_week_report(mock_worksheet)
    assert messages == ["No valid reports"]
