from typing import Optional


def normalize_text(value: Optional[str]) -> Optional[str]:
    """
    Normalize text for comparison.

    The original value is preserved elsewhere.
    This function only removes surrounding whitespace
    and converts text to lowercase.
    """

    if value is None:
        return None

    normalized = value.strip().lower()

    return normalized if normalized else None