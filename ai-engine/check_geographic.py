from assignment_engine.rules.geographic import calculate_zone_score


test_cases = [
    ("centro", "centro"),
    ("centro", "occidente"),
    ("ant", "antioquia"),
    ("bogotá", "centro"),
    (None, "centro"),
    (None, None),
    ("occidente", "occidente"),
]


print("=== PRUEBA REGLA GEOGRÁFICA ===")

for record_zone, user_zone in test_cases:
    score = calculate_zone_score(
        record_zone,
        user_zone,
    )

    print(
        "Registro:",
        repr(record_zone),
        "| Usuario:",
        repr(user_zone),
        "| Score:",
        score,
    )