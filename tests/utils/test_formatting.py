"""
Unit tests for formatting and text manipulation utilities.
"""

from utils.formatting import (
    get_clean_val,
    capitalize_text,
    get_unique_non_empty,
    split_message_smartly,
    sanitize_markdown,
)


def test_get_clean_val_valid():
    rows = [["", "  Topic A  ", "100"]]
    assert get_clean_val(rows, 0, 1) == "Topic A"


def test_get_clean_val_out_of_bounds():
    rows = [["A", "B"]]
    assert get_clean_val(rows, 1, 0) is None
    assert get_clean_val(rows, 0, 5) is None


def test_capitalize_text():
    assert capitalize_text("fps drop") == "Fps drop"
    assert capitalize_text("  ui issue") == "Ui issue"
    assert capitalize_text("") == ""


def test_get_unique_non_empty():
    items = [
        {"obs": "Lag"},
        {"obs": "Crash"},
        {"obs": "Lag"},
        {"obs": None},
    ]
    result = get_unique_non_empty(items, "obs")
    assert result == ["Lag", "Crash"]


def test_sanitize_markdown():
    raw_text = "**Bold** and *Italic* and ~~Strikethrough~~"
    assert sanitize_markdown(raw_text) == "Bold and Italic and Strikethrough"


def test_split_message_smartly_under_limit():
    short_text = "This is a short message."
    assert split_message_smartly(short_text, max_limit=100) == [short_text]


def test_split_message_smartly_over_limit():
    paragraphs = ["Paragraph 1 " * 10, "Paragraph 2 " * 10]
    full_text = "\n\n".join(paragraphs)
    chunks = split_message_smartly(full_text, max_limit=150)

    assert len(chunks) == 2
    assert "Paragraph 1" in chunks[0]
    assert "Paragraph 2" in chunks[1]
