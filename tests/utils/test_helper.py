"""
Unit tests for utility functions and helper methods.
"""

from utils.helper import extract_row_data


def test_extract_row_data_standard_complete_row():
    row = [
        "2026-08-17",
        "https://screenshot.link/1",
        "UI / UX",
        "Button is misaligned",
        "Users cannot click submit",
        "Fix CSS alignment",
        "120",
    ]
    result = extract_row_data(row)
    assert result == (
        "2026-08-17",
        "https://screenshot.link/1",
        "UI / UX",
        "Button is misaligned",
        "Users cannot click submit",
        "Fix CSS alignment",
        "120",
    )


def test_extract_row_data_strips_whitespace():
    row = [
        "  2026-08-17  ",
        " https://screenshot.link/1 ",
        " UI / UX ",
        "\tButton is misaligned\n",
        " Users cannot click submit ",
        " Fix CSS alignment ",
        " 120 ",
    ]
    result = extract_row_data(row)
    assert result == (
        "2026-08-17",
        "https://screenshot.link/1",
        "UI / UX",
        "Button is misaligned",
        "Users cannot click submit",
        "Fix CSS alignment",
        "120",
    )


def test_extract_row_data_short_row_padding():
    row = ["2026-08-17", "https://screenshot.link/1", "UI / UX"]
    result = extract_row_data(row)
    assert result == (
        "2026-08-17",
        "https://screenshot.link/1",
        "UI / UX",
        "",
        "",
        "",
        "",
    )


def test_extract_row_data_empty_row():
    row = []
    result = extract_row_data(row)
    assert result == ("", "", "", "", "", "", "")


def test_extract_row_data_ignores_extra_columns():
    row = [
        "2026-08-17",
        "https://screenshot.link/1",
        "UI / UX",
        "Observation",
        "Consequence",
        "Solution",
        "100",
        "Extra Column 1",
        "Extra Column 2",
    ]
    result = extract_row_data(row)
    assert len(result) == 7
    assert result[6] == "100"
