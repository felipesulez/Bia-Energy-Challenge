def calculate_load_score(
    current_load: int,
    maximum_capacity: int,
) -> float:
    """
    Calculate the load-balance score.

    A user with no current load receives the maximum
    score of 40. A user at full capacity receives 0.

    Formula:
        score = 40 * (1 - current_load / maximum_capacity)
    """

    if maximum_capacity <= 0:
        raise ValueError(
            "Maximum capacity must be greater than zero."
        )

    if current_load < 0:
        raise ValueError(
            "Current load cannot be negative."
        )

    if current_load > maximum_capacity:
        raise ValueError(
            "Current load cannot exceed maximum capacity."
        )

    score = 40 * (
        1 - current_load / maximum_capacity
    )

    return float(score)