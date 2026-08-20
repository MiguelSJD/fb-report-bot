"""
General utility functions and helper methods for F&B Bot.
"""

from typing import Any


def extract_row_data(row: list[str]) -> tuple[str, str, str, str, str, str, str]:
    """Safely extracts the first 7 columns from a worksheet row in sequential order:

    [0: Date, 1: Screenshot Link, 2: Topic, 3: Observation, 4: Consequence, 5: Solution, 6: Votes]
    """
    vals = [row[i].strip() if i < len(row) else "" for i in range(7)]
    return (
        vals[0],
        vals[1],
        vals[2],
        vals[3],
        vals[4],
        vals[5],
        vals[6],
    )


def evaluate_weekly_collection_rule(
    category: str,
    subcategory: str,
    obs_sanitized: str,
    seen_cat_subcats: set[tuple[str, str]],
    seen_observations: set[str],
    topics_dict: dict[tuple[str, str], dict[str, Any]],
) -> str:
    """
    Evaluates collection rules for weekly top 10 feedback reports:
    1. Category + Subcategory already collected -> SKIP
    2. Observation seen under a DIFFERENT category -> SKIP
    3. Category + Observation already collected -> APPEND_SUBCAT
    4. Unseen entry or new category with unseen observation & subcategory -> CREATE_CARD
    """
    cat_sub_key = (category, subcategory)
    topic_key = (category, obs_sanitized)

    if cat_sub_key in seen_cat_subcats:
        return "SKIP"

    if obs_sanitized in seen_observations and topic_key not in topics_dict:
        return "SKIP"

    if topic_key in topics_dict:
        return "APPEND_SUBCAT"

    return "CREATE_CARD"
