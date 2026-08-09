"""
Shared string formatting and data extraction utilities for FB Report Bot.
"""


def get_clean_val(rows: list, row_idx: int, col_idx: int) -> str | None:
    """Safely extract and strip a value from a pre-fetched 2D array of sheet values."""
    if row_idx >= len(rows) or col_idx >= len(rows[row_idx]):
        return None

    val = rows[row_idx][col_idx]
    if val is None:
        return None

    str_val = str(val).strip()
    return str_val if str_val else None


def capitalize_text(text: str) -> str:
    """Capitalizes the first letter of a given text while preserving the rest."""
    if not text:
        return ""
    text = text.strip()
    return text[0].upper() + text[1:]


def get_unique_non_empty(items: list[dict], key: str) -> list[str]:
    """Extract non-empty string values for a key from items, preserving insertion order without duplicates."""
    seen = set()
    result = []
    for item in items:
        val = item.get(key)
        if val and val not in seen:
            seen.add(val)
            result.append(val)
    return result


def split_message_smartly(text: str, max_limit: int = 1900) -> list[str]:
    """
    Splits a long message into multiple chunks without breaking sentences or sections mid-word.
    Prefers splitting on section breaks (\n\n) or line breaks (\n).
    """
    if len(text) <= max_limit:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = ""

    for paragraph in paragraphs:
        addition = f"\n\n{paragraph}" if current_chunk else paragraph

        if len(current_chunk) + len(addition) <= max_limit:
            current_chunk += addition
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            if len(paragraph) > max_limit:
                lines = paragraph.split("\n")
                current_chunk = ""
                for line in lines:
                    line_addition = f"\n{line}" if current_chunk else line
                    if len(current_chunk) + len(line_addition) <= max_limit:
                        current_chunk += line_addition
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = line
            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def sanitize_markdown(text: str) -> str:
    """Strip raw Markdown formatting syntax that could break Discord message structure."""
    if not text:
        return ""
    return (
        text.replace("**", "")
        .replace("__", "")
        .replace("*", "")
        .replace("~~", "")
        .strip()
    )
