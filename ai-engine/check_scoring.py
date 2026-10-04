from assignment_engine.rules.scoring import (
    calculate_load_score,
)


test_cases = [
    (0, 40),
    (10, 40),
    (20, 40),
    (30, 40),
    (40, 40),
    (5, 45),
    (3, 38),
    (8, 38),
]


print("=== PRUEBA SCORE DE CARGA ===")

for current_load, maximum_capacity in test_cases:
    score = calculate_load_score(
        current_load,
        maximum_capacity,
    )

    print(
        "Carga:",
        current_load,
        "| Capacidad:",
        maximum_capacity,
        "| Score:",
        round(score, 2),
    )


print()
print("=== PRUEBAS DE VALIDACIÓN ===")


invalid_cases = [
    (-1, 40),
    (41, 40),
    (0, 0),
]


for current_load, maximum_capacity in invalid_cases:
    try:
        calculate_load_score(
            current_load,
            maximum_capacity,
        )

    except ValueError as error:
        print(
            "Caso inválido:",
            (current_load, maximum_capacity),
            "| OK →",
            error,
        )