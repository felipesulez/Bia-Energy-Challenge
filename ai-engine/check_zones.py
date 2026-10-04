from pathlib import Path

from assignment_engine.data.loader import load_users


PROJECT_ROOT = Path(__file__).resolve().parents[1]

USERS_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
    / "usuarios.csv"
)


users = load_users(USERS_FILE)

print("=== ZONAS DE USUARIOS ===")

for user in users:
    print(
        user.id,
        "| original:",
        repr(user.zona),
        "| normalizada:",
        repr(user.zona_normalizada),
    )