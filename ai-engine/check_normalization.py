from assignment_engine.utils.normalization import normalize_text


test_values = [
    "Centro",
    "centro",
    " CENTRO ",
    "Occidente ",
    "ANTIOQUIA",
    "ANT",
    "Bogotá",
    None,
    "   ",
]


print("=== NORMALIZACIÓN ===")

for value in test_values:
    print(
        repr(value),
        "→",
        repr(normalize_text(value)),
    )