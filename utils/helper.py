"""
General utility functions and helper methods for FB Report Bot.
"""


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
