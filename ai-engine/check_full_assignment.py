from datetime import date
from pathlib import Path

from assignment_engine.data.loader import (
    load_absences,
    load_records,
    load_users,
)
from assignment_engine.engine.weighted_rules import (
    WeightedRulesEngine,
)
from assignment_engine.rules.candidate_evaluator import (
    CandidateEvaluator,
)
from assignment_engine.rules.eligibility import (
    EligibilityRule,
    get_active_absence_user_ids,
)
from assignment_engine.services.assignment_service import (
    AssignmentService,
)


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
)

EVALUATION_DATE = date(2026, 10, 3)

EXPECTED_ASSIGNMENTS = 71
EXPECTED_TRACES = 71

EXPECTED_EXACT_ZONE_MATCHES = 55
EXPECTED_FALLBACKS = 11
EXPECTED_MISSING_ZONES = 5
EXPECTED_OUT_OF_ZONE_SELECTIONS = 0

EXPECTED_TOTAL_CAPACITY = 520
EXPECTED_REMAINING_CAPACITY = 449


# Load data
users = load_users(
    DATA_DIR / "usuarios.csv"
)

absences = load_absences(
    DATA_DIR / "ausencias.csv"
)

records = load_records(
    DATA_DIR / "registros.csv"
)


# Build engine
engine = WeightedRulesEngine(
    eligibility_rule=EligibilityRule(),
    candidate_evaluator=CandidateEvaluator(),
)


# Build service
service = AssignmentService(
    engine=engine,
)


# Execute
result = service.assign_pending_records(
    records=records,
    users=users,
    absences=absences,
    evaluation_date=EVALUATION_DATE,
)

assignments = result.assignments
traces = result.traces


print("=== VALIDACIÓN COMPLETA DE ASIGNACIÓN ===")


# 1. Number of assignments
assert len(assignments) == EXPECTED_ASSIGNMENTS

print(
    "✓ Asignaciones:",
    len(assignments),
)


# 2. Number of traces
assert len(traces) == EXPECTED_TRACES

print(
    "✓ Traces:",
    len(traces),
)


# 3. Assignment ↔ Trace correspondence
assert len(assignments) == len(traces)

for assignment, trace in zip(
    assignments,
    traces,
):
    assert (
        assignment.record_id
        == trace.record_id
    )

    assert (
        assignment.usuario_id
        == trace.usuario_seleccionado_id
    )

    assert (
        assignment.metodo
        == trace.metodo
    )

print(
    "✓ Cada assignment corresponde "
    "con su trace"
)


# 4. Unique record assignments
assignment_record_ids = [
    assignment.record_id
    for assignment in assignments
]

assert len(assignment_record_ids) == len(
    set(assignment_record_ids)
)

print(
    "✓ No existen registros asignados más de una vez"
)


# 5. Scores
for assignment in assignments:
    assert (
        assignment.score_total
        == assignment.score_zona
        + assignment.score_carga
    )

    assert 0 <= assignment.score_zona <= 60

    assert 0 <= assignment.score_carga <= 40

    assert 0 <= assignment.score_total <= 100


print("✓ Scores dentro de rango")
print("✓ Score total = score zona + score carga")


# 6. Capacity
for assignment in assignments:
    assert (
        assignment.capacidad_despues
        == assignment.capacidad_antes - 1
    )

    assert (
        assignment.carga_despues
        == assignment.carga_antes + 1
    )

    assert assignment.capacidad_despues >= 0


print("✓ Ninguna asignación supera la capacidad")


# 7. Geographic states
exact_matches = sum(
    assignment.estado_geografico
    == "coincidencia_exacta"
    for assignment in assignments
)

fallbacks = sum(
    assignment.estado_geografico
    == "fallback_sin_candidato_en_zona"
    for assignment in assignments
)

missing_zones = sum(
    assignment.estado_geografico
    == "zona_no_informada"
    for assignment in assignments
)

out_of_zone = sum(
    assignment.estado_geografico
    == "seleccion_fuera_de_zona"
    for assignment in assignments
)


assert exact_matches == EXPECTED_EXACT_ZONE_MATCHES
assert fallbacks == EXPECTED_FALLBACKS
assert missing_zones == EXPECTED_MISSING_ZONES
assert out_of_zone == EXPECTED_OUT_OF_ZONE_SELECTIONS


print(
    "✓ Coincidencias exactas:",
    exact_matches,
)

print(
    "✓ Fallbacks geográficos:",
    fallbacks,
)

print(
    "✓ Zonas no informadas:",
    missing_zones,
)

print(
    "✓ Selecciones fuera de zona:",
    out_of_zone,
)


# 8. Trace consistency
for assignment, trace in zip(
    assignments,
    traces,
):
    assert (
        assignment.score_zona
        == trace.candidatos[0].score_zona
    )

    assert (
        assignment.score_carga
        == trace.candidatos[0].score_carga
    )

    assert (
        assignment.score_total
        == trace.candidatos[0].score_total
    )

    assert (
        trace.candidatos[0].usuario_id
        == trace.usuario_seleccionado_id
    )


print(
    "✓ El primer candidato del trace "
    "corresponde al usuario seleccionado"
)

print(
    "✓ Scores del assignment consistentes "
    "con el candidato seleccionado"
)


# 9. Global capacity of eligible users
active_absence_user_ids = get_active_absence_user_ids(
    absences,
    EVALUATION_DATE,
)

eligibility_rule = EligibilityRule()

eligible_users = eligibility_rule.filter_eligible(
    users,
    active_absence_user_ids,
)


initial_capacity = sum(
    user.capacidad_maxima
    for user in eligible_users
)


final_capacity = sum(
    user.capacidad_disponible
    for user in eligible_users
    if user.capacidad_disponible is not None
)


consumed_capacity = (
    initial_capacity
    - final_capacity
)


assert initial_capacity == EXPECTED_TOTAL_CAPACITY

assert final_capacity == EXPECTED_REMAINING_CAPACITY

assert consumed_capacity == EXPECTED_ASSIGNMENTS


print(
    "✓ Capacidad inicial:",
    initial_capacity,
)

print(
    "✓ Capacidad consumida:",
    consumed_capacity,
)

print(
    "✓ Capacidad restante:",
    final_capacity,
)


print("\n=== VALIDACIÓN COMPLETADA ===")
print("✓ Todos los controles pasaron correctamente")