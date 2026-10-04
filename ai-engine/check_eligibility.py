from datetime import date
from pathlib import Path

from assignment_engine.data.loader import (
    load_absences,
    load_users,
)
from assignment_engine.rules.eligibility import (
    EligibilityRule,
    get_active_absence_user_ids,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

USERS_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
    / "usuarios.csv"
)

ABSENCES_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
    / "ausencias.csv"
)

EVALUATION_DATE = date(2026, 10, 3)


users = load_users(USERS_FILE)
absences = load_absences(ABSENCES_FILE)

active_absence_user_ids = get_active_absence_user_ids(
    absences,
    EVALUATION_DATE,
)

eligibility_rule = EligibilityRule()

eligible_users = eligibility_rule.filter_eligible(
    users,
    active_absence_user_ids,
)

print("=== USUARIOS ELEGIBLES ===")

for user in eligible_users:
    print(
        user.id,
        "-",
        user.nombre,
        "|",
        user.rol,
        "| capacidad:",
        user.capacidad_maxima,
    )

print()
print("Total:", len(eligible_users))