from typing import Optional


def calculate_zone_score(
    record_zone: Optional[str],
    user_zone: Optional[str],
) -> float:
    """
    Calculate the geographic score for a record-user pair.

    An exact normalized zone match receives 60 points.
    Otherwise, the geographic score is 0.

    No semantic mapping is performed.
    For example, "ant" is not considered equivalent to
    "antioquia".
    """

    if (
        record_zone is not None
        and user_zone is not None
        and record_zone == user_zone
    ):
        return 60.0

    return 0.0