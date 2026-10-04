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
        zona="occidente",
        segmento_experto="pyme",
        capacidad_maxima=40,
        fecha_ingreso=date(2024, 1, 1),
        activo=True,
        carga_actual=5,
    ),
    User(
        id=30,
        nombre="Usuario C",
        email="c@example.com",
        rol="vendedor",
        equipo_id=1,
        zona="centro",
        segmento_experto="corporativo",
        capacidad_maxima=40,
        fecha_ingreso=date(2024, 1, 1),
        activo=True,
        carga_actual=20,
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


print("=== PRUEBA WEIGHTED RULES ENGINE ===")

if assignment is None:
    print("No se realizó asignación.")

else:
    print("Registro:", assignment.record_id)
    print("Usuario seleccionado:", assignment.usuario_id)
    print("Nombre:", assignment.usuario_nombre)
    print("Score zona:", assignment.score_zona)
    print("Score carga:", round(assignment.score_carga, 2))
    print("Score total:", round(assignment.score_total, 2))
    print("Carga antes:", assignment.carga_antes)
    print("Carga después:", assignment.carga_despues)
    print(
        "Capacidad antes:",
        assignment.capacidad_antes,
    )
    print(
        "Capacidad después:",
        assignment.capacidad_despues,
    )
    print(
        "Estado geográfico:",
        assignment.estado_geografico,
    )
    print("Razón:", assignment.razon)


print()
print("=== ESTADO DE USUARIOS ===")

for user in users:
    print(
        user.id,
        "| carga:",
        user.carga_actual,
        "| disponible:",
        user.capacidad_disponible,
    )