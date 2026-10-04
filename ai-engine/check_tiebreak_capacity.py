from datetime import date, datetime

from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.engine.weighted_rules import (
    WeightedRulesEngine,
)
from assignment_engine.rules.candidate_evaluator import (
    CandidateEvaluator,
)
from assignment_engine.rules.eligibility import EligibilityRule


record = Record(
    id=1,
    razon_social="Empresa de prueba",
    nit="900123456-1",
    sector="servicios",
    empleados=50,
    ingresos_estimados=1_000_000_000,
    ciudad="Bogotá",
    zona="Centro",
    fuente="web",
    notas=None,
    estado="nuevo",
    fecha_creacion=datetime(2026, 10, 1),
)


users = [
    User(
        id=10,
        nombre="Usuario A",
        email="a@example.com",
        rol="vendedor",
        equipo_id=1,
        zona="centro",
        segmento_experto="industrial",
        capacidad_maxima=40,
        fecha_ingreso=date(2024, 1, 1),
        activo=True,
        carga_actual=10,
    ),
    User(
        id=20,
        nombre="Usuario B",
        email="b@example.com",
        rol="vendedor",
        equipo_id=1,
        zona="centro",
        segmento_experto="pyme",
        capacidad_maxima=40,
        fecha_ingreso=date(2024, 1, 1),
        activo=True,
        carga_actual=10,
    ),
]


engine = WeightedRulesEngine(
    eligibility_rule=EligibilityRule(),
    candidate_evaluator=CandidateEvaluator(),
)


assignment = engine.assign(
    record=record,
    users=users,
    active_absence_user_ids=set(),
)


print("=== PRUEBA DE DESEMPATE: CAPACIDAD ===")

for user in users:
    print(
        user.id,
        "| score esperado:",
        60.0 + (
            40 * (1 - user.carga_actual / user.capacidad_maxima)
        ),
        "| capacidad disponible:",
        user.capacidad_disponible,
    )


print()

if assignment is None:
    print("No se realizó asignación.")

else:
    print("Usuario seleccionado:", assignment.usuario_id)
    print("Nombre:", assignment.usuario_nombre)
    print("Score zona:", assignment.score_zona)
    print("Score carga:", round(assignment.score_carga, 2))
    print("Score total:", round(assignment.score_total, 2))
    print(
        "Capacidad disponible antes:",
        assignment.capacidad_antes,
    )