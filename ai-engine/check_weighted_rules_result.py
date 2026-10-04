from assignment_engine.domain.assignment_result import AssignmentResult
from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.rules.candidate_evaluator import CandidateEvaluator
from assignment_engine.rules.eligibility import EligibilityRule


record = Record(
    id=1,
    razon_social="Empresa de prueba",
    nit="900123456-1",
    sector="Comercio",
    empleados=10,
    ingresos_estimados=1000000000.0,
    ciudad="Bogotá",
    zona="Centro",
    fuente="prueba",
    notas=None,
    estado="nuevo",
    fecha_creacion=None,
)


users = [
    User(
        id=10,
        nombre="Usuario A",
        email="usuario.a@test.com",
        rol="vendedor",
        equipo_id=1,
        zona="Centro",
        segmento_experto="corporativo",
        capacidad_maxima=40,
        fecha_ingreso=None,
        activo=True,
        carga_actual=10,
    ),
    User(
        id=20,
        nombre="Usuario B",
        email="usuario.b@test.com",
        rol="vendedor",
        equipo_id=1,
        zona="Occidente",
        segmento_experto="pyme",
        capacidad_maxima=40,
        fecha_ingreso=None,
        activo=True,
        carga_actual=5,
    ),
    User(
        id=30,
        nombre="Usuario C",
        email="usuario.c@test.com",
        rol="vendedor",
        equipo_id=1,
        zona="Centro",
        segmento_experto="industrial",
        capacidad_maxima=40,
        fecha_ingreso=None,
        activo=True,
        carga_actual=20,
    ),
]


engine = WeightedRulesEngine(
    eligibility_rule=EligibilityRule(),
    candidate_evaluator=CandidateEvaluator(),
)


result = engine.assign(
    record=record,
    users=users,
    active_absence_user_ids=set(),
)


print("=== PRUEBA WEIGHTED RULES → ASSIGNMENT RESULT ===")

assert result is not None
assert isinstance(result, AssignmentResult)

print("✓ El resultado es un AssignmentResult")

print("\n=== ASSIGNMENT ===")

assignment = result.assignment

print("Registro:", assignment.record_id)
print("Usuario asignado:", assignment.usuario_id)
print("Nombre:", assignment.usuario_nombre)
print("Método:", assignment.metodo)
print("Score zona:", assignment.score_zona)
print("Score carga:", assignment.score_carga)
print("Score total:", assignment.score_total)
print("Carga antes:", assignment.carga_antes)
print("Carga después:", assignment.carga_despues)
print("Estado geográfico:", assignment.estado_geografico)


print("\n=== TRACE ===")

trace = result.trace

print("Registro:", trace.record_id)
print("Método:", trace.metodo)
print(
    "Usuario seleccionado:",
    trace.usuario_seleccionado_id,
)
print(
    "Candidatos evaluados:",
    len(trace.candidatos),
)
print(
    "Estado geográfico:",
    trace.estado_geografico,
)
print("Razón:", trace.razon)


print("\n=== RANKING ===")

for position, candidate in enumerate(
    trace.candidatos,
    start=1,
):
    print(
        f"#{position} "
        f"Usuario {candidate.usuario_id} "
        f"| Score zona: {candidate.score_zona:.2f} "
        f"| Score carga: {candidate.score_carga:.2f} "
        f"| Score total: {candidate.score_total:.2f} "
        f"| Capacidad disponible: "
        f"{candidate.capacidad_disponible}"
    )


print("\n=== VALIDACIONES ===")

assert assignment.record_id == trace.record_id

assert (
    assignment.usuario_id
    == trace.usuario_seleccionado_id
)

assert assignment.metodo == trace.metodo

assert (
    assignment.estado_geografico
    == trace.estado_geografico
)

assert assignment.score_total == (
    assignment.score_zona
    + assignment.score_carga
)

assert trace.candidatos[0].usuario_id == 10

assert users[0].carga_actual == 11
assert users[0].capacidad_disponible == 29

print("✓ Assignment y Trace corresponden al mismo registro")
print("✓ Assignment y Trace corresponden al mismo usuario")
print("✓ Assignment y Trace utilizan el mismo método")
print("✓ Estado geográfico consistente")
print("✓ Score total consistente")
print("✓ Ranking determinístico correcto")
print("✓ La carga del usuario seleccionado se actualizó")
print("✓ La capacidad disponible se actualizó")

print("\n=== PRUEBA COMPLETADA ===")